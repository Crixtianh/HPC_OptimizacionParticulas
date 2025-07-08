#!/usr/bin/env python3
"""
ETAPA 6: SISTEMA DE ORQUESTACIÓN CON COLA DE TAREAS
==================================================

Implementa un maestro elástico con cola de tareas distribuida:
- Cola de tareas con algoritmo y parámetros
- Distribución automática de tareas
- Almacenamiento de tiempos de procesamiento
- Balanceamiento de carga inteligente
- Recuperación de tareas fallidas
- Métricas de rendimiento por worker

Características nuevas:
- Task Queue Management
- Performance Tracking
- Load Balancing
- Fault Recovery
- Results Storage
"""

import requests
import json
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from config_manager import get_config
import signal
import sys
from dataclasses import dataclass, asdict
from collections import deque
import queue
import uuid
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/elastic_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Estados de las tareas"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """Clase para representar una tarea"""
    id: str
    algorithm: str  # benchmark.py, benchmark_cython.py
    parameters: Dict[str, Any]
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    assigned_worker: Optional[str] = None
    created_at: datetime = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para JSON"""
        data = asdict(self)
        # Convertir datetime a string
        for field in ['created_at', 'assigned_at', 'started_at', 'completed_at']:
            if data[field]:
                data[field] = data[field].isoformat()
        # Convertir enum a string
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Crear desde diccionario"""
        # Convertir strings a datetime
        for field in ['created_at', 'assigned_at', 'started_at', 'completed_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convertir string a enum
        if isinstance(data.get('status'), str):
            data['status'] = TaskStatus(data['status'])
        
        return cls(**data)

@dataclass
class WorkerStatus:
    """Clase para almacenar el estado de un worker"""
    id: str
    ip: str
    port: int
    status: str = "unknown"
    last_ping: Optional[datetime] = None
    last_successful_ping: Optional[datetime] = None
    consecutive_failures: int = 0
    total_tasks_completed: int = 0
    average_response_time: float = 0.0
    response_times: deque = None
    current_task: Optional[str] = None
    processing_power: float = 1.0
    task_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = deque(maxlen=10)
        if self.task_history is None:
            self.task_history = []
    
    def update_response_time(self, response_time: float):
        """Actualizar tiempo de respuesta"""
        self.response_times.append(response_time)
        self.average_response_time = sum(self.response_times) / len(self.response_times)
    
    def add_task_result(self, task_id: str, execution_time: float, success: bool):
        """Agregar resultado de tarea"""
        self.task_history.append({
            "task_id": task_id,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 50 resultados
        if len(self.task_history) > 50:
            self.task_history = self.task_history[-50:]
        
        if success:
            self.total_tasks_completed += 1
    
    def get_average_task_time(self) -> float:
        """Obtener tiempo promedio de ejecución de tareas"""
        successful_tasks = [t for t in self.task_history if t["success"]]
        if not successful_tasks:
            return 0.0
        return sum(t["execution_time"] for t in successful_tasks) / len(successful_tasks)
    
    def get_success_rate(self) -> float:
        """Obtener tasa de éxito de tareas"""
        if not self.task_history:
            return 1.0
        successful = sum(1 for t in self.task_history if t["success"])
        return successful / len(self.task_history)
    
    def is_healthy(self) -> bool:
        """Verificar si el worker está saludable"""
        if self.status != "active":
            return False
        
        # Considerar unhealthy si han pasado más de 30 segundos sin ping exitoso
        if self.last_successful_ping:
            time_since_last_ping = datetime.now() - self.last_successful_ping
            if time_since_last_ping > timedelta(seconds=30):
                return False
        
        # Considerar unhealthy si hay muchos fallos consecutivos
        return self.consecutive_failures < 3
    
    def is_available(self) -> bool:
        """Verificar si el worker está disponible para tareas"""
        return self.is_healthy() and self.current_task is None
    
    def calculate_load_score(self) -> float:
        """Calcular score de carga (menor es mejor)"""
        score = 0.0
        
        # Factor 1: Tiempo de respuesta (40%)
        if self.average_response_time > 0:
            score += self.average_response_time * 0.4
        
        # Factor 2: Carga actual (30%)
        current_load = 1.0 if self.current_task else 0.0
        score += current_load * 0.3
        
        # Factor 3: Tiempo promedio de tareas (30%)
        avg_task_time = self.get_average_task_time()
        if avg_task_time > 0:
            score += (avg_task_time / 60.0) * 0.3  # Normalizar a minutos
        
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para JSON"""
        return {
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "status": self.status,
            "last_ping": self.last_ping.isoformat() if self.last_ping else None,
            "last_successful_ping": self.last_successful_ping.isoformat() if self.last_successful_ping else None,
            "consecutive_failures": self.consecutive_failures,
            "total_tasks_completed": self.total_tasks_completed,
            "average_response_time": self.average_response_time,
            "current_task": self.current_task,
            "processing_power": self.processing_power,
            "is_healthy": self.is_healthy(),
            "is_available": self.is_available(),
            "task_history": self.task_history[-10:],  # Solo últimos 10 para JSON
            "average_task_time": self.get_average_task_time(),
            "success_rate": self.get_success_rate(),
            "load_score": self.calculate_load_score()
        }

class TaskManager:
    """Gestor de cola de tareas"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.pending_queue = queue.PriorityQueue()
        self.task_lock = threading.RLock()
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def add_task(self, algorithm: str, parameters: Dict[str, Any], priority: int = 1) -> str:
        """Agregar tarea a la cola"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            algorithm=algorithm,
            parameters=parameters,
            priority=priority
        )
        
        with self.task_lock:
            self.tasks[task_id] = task
            # Prioridad negativa para queue (menor número = mayor prioridad)
            self.pending_queue.put((-priority, task_id))
        
        logger.info(f"📋 Tarea agregada: {task_id} ({algorithm})")
        return task_id
    
    def get_next_task(self) -> Optional[Task]:
        """Obtener siguiente tarea de la cola"""
        with self.task_lock:
            if self.pending_queue.empty():
                return None
            
            try:
                _, task_id = self.pending_queue.get_nowait()
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    if task.status == TaskStatus.PENDING:
                        return task
                return None
            except queue.Empty:
                return None
    
    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """Actualizar estado de tarea"""
        with self.task_lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = status
            
            # Actualizar campos específicos
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # Actualizar timestamps
            if status == TaskStatus.ASSIGNED:
                task.assigned_at = datetime.now()
            elif status == TaskStatus.RUNNING:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
                if task.started_at:
                    task.execution_time = (task.completed_at - task.started_at).total_seconds()
            
            logger.info(f"🔄 Tarea {task_id} cambió a estado: {status.value}")
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de tareas"""
        with self.task_lock:
            stats = {
                "total_tasks": len(self.tasks),
                "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                "assigned": sum(1 for t in self.tasks.values() if t.status == TaskStatus.ASSIGNED),
                "running": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
                "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
                "queue_size": self.pending_queue.qsize()
            }
            
            # Estadísticas de tiempo
            completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED and t.execution_time]
            if completed_tasks:
                execution_times = [t.execution_time for t in completed_tasks]
                stats["avg_execution_time"] = sum(execution_times) / len(execution_times)
                stats["min_execution_time"] = min(execution_times)
                stats["max_execution_time"] = max(execution_times)
            else:
                stats["avg_execution_time"] = 0.0
                stats["min_execution_time"] = 0.0
                stats["max_execution_time"] = 0.0
            
            return stats
    
    def save_results(self):
        """Guardar resultados de tareas"""
        with self.task_lock:
            results_file = os.path.join(self.results_dir, f"task_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "tasks": [task.to_dict() for task in self.tasks.values()],
                "statistics": self.get_task_stats()
            }
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"💾 Resultados guardados en: {results_file}")

class ElasticOrchestratorV6:
    """Orquestador elástico versión 6 con cola de tareas"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Inicializar el orquestador elástico v6"""
        self.env_config = get_config()
        self.running = False
        self.workers: Dict[str, WorkerStatus] = {}
        self.worker_lock = threading.RLock()
        self.task_manager = TaskManager()
        
        # Configuración desde .env
        self.docker_config = self.env_config.get_docker_config()
        self.timeout_config = self.env_config.get_timeout_config()
        self.benchmark_config = self.env_config.get_benchmark_config()
        
        # Configuración de monitoreo
        self.ping_interval = 5
        self.health_check_interval = 10
        self.task_distribution_interval = 2
        self.max_ping_failures = 5
        
        # Configuración de carga automática de tareas
        self.auto_task_check_interval = 10  # Revisar cada 10 segundos
        self.task_queue_dir = "task_queues"
        self.processed_files = set()  # Archivos ya procesados
        
        # Crear directorio de colas si no existe
        os.makedirs(self.task_queue_dir, exist_ok=True)
        
        # Cargar workers desde configuración
        self._load_workers_config(config_file)
        
        # Hilos de monitoreo
        self.worker_monitor_thread = None
        self.task_monitor_thread = None
        self.auto_task_loader_thread = None  # Solo carga archivos manuales
        
        # NO crear generador automático - Solo procesamiento manual
        self.auto_task_generator = None
        logger.info("📋 Modo MANUAL: Solo procesará archivos agregados manualmente")
        
        # Estadísticas
        self.stats = {
            "total_pings": 0,
            "successful_pings": 0,
            "failed_pings": 0,
            "workers_discovered": 0,
            "workers_lost": 0,
            "tasks_distributed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "uptime_start": datetime.now()
        }
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 Orquestador elástico v6 inicializado")
    
    def _load_workers_config(self, config_file: Optional[str] = None):
        """Cargar configuración de workers"""
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            workers_list = config.get('workers', [])
        else:
            workers_config = self.env_config.get_workers_config()
            workers_list = workers_config.get('workers', [])
        
        # Crear objetos WorkerStatus
        for worker_data in workers_list:
            worker_id = worker_data['id']
            processing_power = 1.0
            
            # Asignar poder de procesamiento específico
            if worker_id == 'worker-01':
                processing_power = 1.0  # Worker 1 tiene más poder
            elif worker_id == 'worker-02':
                processing_power = 0.8  # Worker 2 tiene menos poder pero es más rápido
            
            self.workers[worker_id] = WorkerStatus(
                id=worker_id,
                ip=worker_data['ip'],
                port=worker_data['port'],
                processing_power=processing_power
            )
        
        logger.info(f"📋 Cargados {len(self.workers)} workers desde configuración")
    
    def _signal_handler(self, signum, frame):
        """Manejar señales de terminación"""
        logger.info(f"🛑 Recibida señal {signum}, terminando...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Iniciar el orquestador elástico"""
        if self.running:
            logger.warning("⚠️  El orquestador ya está en ejecución")
            return
        
        self.running = True
        logger.info("🎯 Iniciando orquestador elástico v6...")
        
        # Crear directorio de logs
        os.makedirs('logs', exist_ok=True)
        
        # Iniciar MEMORIA 1: Monitor de Workers
        self.worker_monitor_thread = threading.Thread(
            target=self._worker_monitor_loop,
            name="WorkerMonitor",
            daemon=True
        )
        self.worker_monitor_thread.start()
        logger.info("🧠 MEMORIA 1: Monitor de Workers iniciado")
        
        # Iniciar MEMORIA 2: Monitor de Tareas y Distribuidor
        self.task_monitor_thread = threading.Thread(
            target=self._task_monitor_loop,
            name="TaskMonitor",
            daemon=True
        )
        self.task_monitor_thread.start()
        logger.info("🧠 MEMORIA 2: Monitor de Tareas y Distribuidor iniciado")
        
        # Iniciar MEMORIA 3: Cargador Automático de Tareas
        self.auto_task_loader_thread = threading.Thread(
            target=self._auto_task_loader_loop,
            name="AutoTaskLoader",
            daemon=True
        )
        self.auto_task_loader_thread.start()
        logger.info("🧠 MEMORIA 3: Cargador Automático de Tareas iniciado")
        
        # NO iniciar generador automático - Solo modo manual
        logger.info("📋 Modo MANUAL activado: Coloca archivos .json en task_queues/")
        
        logger.info("✅ Orquestador elástico v6 iniciado exitosamente")
    
    def stop(self):
        """Detener el orquestador elástico"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador elástico v6...")
        self.running = False
        
        # Guardar resultados antes de terminar
        self.task_manager.save_results()
        
        # Esperar a que terminen los hilos
        if self.worker_monitor_thread and self.worker_monitor_thread.is_alive():
            self.worker_monitor_thread.join(timeout=5)
        
        if self.task_monitor_thread and self.task_monitor_thread.is_alive():
            self.task_monitor_thread.join(timeout=5)
            
        if self.auto_task_loader_thread and self.auto_task_loader_thread.is_alive():
            self.auto_task_loader_thread.join(timeout=5)
        
        logger.info("✅ Orquestador elástico v6 detenido")
    
    def _worker_monitor_loop(self):
        """MEMORIA 1: Loop principal del monitor de workers"""
        logger.info("🔄 Iniciando loop de monitoreo de workers...")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Ping a todos los workers
                self._ping_all_workers()
                
                # Verificar salud de workers
                self._check_worker_health()
                
                # Actualizar estadísticas
                self._update_stats()
                
                # Guardar estado
                self._save_worker_state()
                
                # Calcular tiempo de sleep
                elapsed = time.time() - start_time
                sleep_time = max(0, self.ping_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"❌ Error en monitor de workers: {e}")
                time.sleep(1)
    
    def _task_monitor_loop(self):
        """MEMORIA 2: Loop principal del monitor de tareas y distribución"""
        logger.info("🔄 Iniciando loop de monitoreo de tareas y distribución...")
        
        while self.running:
            try:
                # Distribuir tareas pendientes
                self._distribute_tasks()
                
                # Verificar tareas en ejecución
                self._check_running_tasks()
                
                # Recuperar tareas fallidas
                self._recover_failed_tasks()
                
                # Guardar resultados periódicamente
                if int(time.time()) % 300 == 0:  # Cada 5 minutos
                    self.task_manager.save_results()
                
                time.sleep(self.task_distribution_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en monitor de tareas: {e}")
                time.sleep(1)
    
    def _auto_task_loader_loop(self):
        """MEMORIA 3: Loop para cargar automáticamente tareas desde archivos"""
        logger.info("🔄 Iniciando loop de carga automática de tareas...")
        
        while self.running:
            try:
                # Buscar archivos de tareas pendientes
                self._load_pending_task_files()
                
                # Esperar antes de la próxima verificación
                time.sleep(self.auto_task_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en carga automática de tareas: {e}")
                time.sleep(5)
    
    def _load_pending_task_files(self):
        """Cargar archivos de tareas pendientes"""
        if not os.path.exists(self.task_queue_dir):
            return
        
        task_files = []
        for filename in os.listdir(self.task_queue_dir):
            if filename.endswith('.json') and filename not in self.processed_files:
                filepath = os.path.join(self.task_queue_dir, filename)
                task_files.append((filename, filepath))
        
        # Procesar archivos encontrados
        for filename, filepath in task_files:
            try:
                self._process_task_file(filename, filepath)
            except Exception as e:
                logger.error(f"❌ Error procesando archivo {filename}: {e}")
    
    def _process_task_file(self, filename: str, filepath: str):
        """Procesar un archivo de tareas"""
        logger.info(f"📁 Procesando archivo de tareas: {filename}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            if not tasks:
                logger.warning(f"⚠️  Archivo {filename} no contiene tareas")
                self.processed_files.add(filename)
                return
            
            # Agregar tareas a la cola
            added_count = 0
            for task_data in tasks:
                if self._add_task_from_data(task_data):
                    added_count += 1
            
            logger.info(f"✅ Cargadas {added_count}/{len(tasks)} tareas desde {filename}")
            
            # Marcar archivo como procesado
            self.processed_files.add(filename)
            
            # Mover archivo a subdirectorio procesado
            self._move_processed_file(filepath, filename)
            
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo {filename}: {e}")
    
    def _add_task_from_data(self, task_data: Dict[str, Any]) -> bool:
        """Agregar tarea desde datos JSON"""
        try:
            # Extraer información de la tarea
            task_id = task_data.get('task_id')
            algorithm = task_data.get('algorithm')
            parameters = task_data.get('parameters', {})
            priority = task_data.get('priority', 1)
            
            # Validar datos requeridos
            if not task_id or not algorithm:
                logger.warning(f"⚠️  Tarea inválida: falta task_id o algorithm")
                return False
            
            # Verificar que la tarea no exista ya
            if task_id in self.task_manager.tasks:
                logger.debug(f"🔄 Tarea {task_id} ya existe, omitiendo")
                return False
            
            # Crear tarea
            task = Task(
                id=task_id,
                algorithm=algorithm,
                parameters=parameters,
                priority=priority
            )
            
            # Agregar campos adicionales si están presentes
            if 'description' in task_data:
                task.description = task_data['description']
            if 'created_at' in task_data:
                try:
                    task.created_at = datetime.fromisoformat(task_data['created_at'])
                except:
                    pass
            
            # Agregar tarea al gestor
            with self.task_manager.task_lock:
                self.task_manager.tasks[task_id] = task
                # Agregar a cola de pendientes
                self.task_manager.pending_queue.put((-priority, task_id))
            
            logger.debug(f"➕ Tarea agregada automáticamente: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error agregando tarea: {e}")
            return False
    
    def _move_processed_file(self, filepath: str, filename: str):
        """Mover archivo procesado a subdirectorio"""
        try:
            processed_dir = os.path.join(self.task_queue_dir, "processed")
            os.makedirs(processed_dir, exist_ok=True)
            
            # Agregar timestamp al nombre
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            new_filepath = os.path.join(processed_dir, new_filename)
            
            # Mover archivo
            os.rename(filepath, new_filepath)
            logger.debug(f"📦 Archivo movido a: processed/{new_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error moviendo archivo procesado: {e}")
    
    def get_auto_task_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de carga automática"""
        stats = {
            "processed_files": len(self.processed_files),
            "pending_files": 0,
            "queue_directory": self.task_queue_dir,
            "auto_generation_active": False,
            "mode": "MANUAL"
        }
        
        # Contar archivos pendientes
        if os.path.exists(self.task_queue_dir):
            all_files = [f for f in os.listdir(self.task_queue_dir) if f.endswith('.json')]
            stats["pending_files"] = len([f for f in all_files if f not in self.processed_files])
        
        # Siempre en modo manual
        stats["auto_generation_active"] = False
        
        return stats

    def _ping_all_workers(self):
        """Hacer ping a todos los workers"""
        with self.worker_lock:
            for worker_id, worker in self.workers.items():
                self._ping_worker(worker)
    
    def _ping_worker(self, worker: WorkerStatus):
        """Hacer ping a un worker específico"""
        try:
            start_time = time.time()
            url = f"http://{worker.ip}:{worker.port}/ping"
            
            response = requests.get(url, timeout=self.timeout_config['http_timeout'])
            response_time = time.time() - start_time
            
            self.stats["total_pings"] += 1
            
            if response.status_code == 200:
                # Ping exitoso
                old_status = worker.status
                worker.status = "active"
                worker.last_ping = datetime.now()
                worker.last_successful_ping = datetime.now()
                worker.consecutive_failures = 0
                worker.update_response_time(response_time)
                
                self.stats["successful_pings"] += 1
                
                if old_status != "active":
                    logger.info(f"🔗 Worker {worker.id} conectado")
                    self.stats["workers_discovered"] += 1
                    
            else:
                self._handle_ping_failure(worker, f"HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self._handle_ping_failure(worker, "Connection refused")
        except requests.exceptions.Timeout:
            self._handle_ping_failure(worker, "Timeout")
        except Exception as e:
            self._handle_ping_failure(worker, str(e))
    
    def _handle_ping_failure(self, worker: WorkerStatus, error: str):
        """Manejar fallo de ping"""
        worker.last_ping = datetime.now()
        worker.consecutive_failures += 1
        self.stats["failed_pings"] += 1
        
        # Cambiar estado según número de fallos
        if worker.consecutive_failures >= self.max_ping_failures:
            if worker.status == "active":
                logger.warning(f"⚠️  Worker {worker.id} perdido después de {worker.consecutive_failures} fallos")
                self.stats["workers_lost"] += 1
                
                # Marcar tarea actual como fallida si existe
                if worker.current_task:
                    self.task_manager.update_task_status(
                        worker.current_task,
                        TaskStatus.FAILED,
                        error=f"Worker {worker.id} perdido"
                    )
                    worker.current_task = None
                    
            worker.status = "inactive"
        else:
            worker.status = "unstable"
    
    def _check_worker_health(self):
        """Verificar salud general de workers"""
        with self.worker_lock:
            active_workers = [w for w in self.workers.values() if w.status == "active"]
            healthy_workers = [w for w in self.workers.values() if w.is_healthy()]
            
            if len(active_workers) != len(healthy_workers):
                logger.warning(f"⚠️  {len(active_workers)} workers activos, {len(healthy_workers)} saludables")
    
    def _distribute_tasks(self):
        """Distribuir tareas a workers disponibles"""
        # Obtener workers disponibles
        available_workers = [w for w in self.workers.values() if w.is_available()]
        
        if not available_workers:
            return
        
        # Distribuir tareas mientras haya workers disponibles
        for worker in available_workers:
            task = self.task_manager.get_next_task()
            if not task:
                break
            
            # Asignar tarea al worker
            self._assign_task_to_worker(task, worker)
    
    def _assign_task_to_worker(self, task: Task, worker: WorkerStatus):
        """Asignar tarea a un worker específico"""
        try:
            # Actualizar estado de tarea
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.ASSIGNED,
                assigned_worker=worker.id
            )
            
            # Actualizar estado del worker
            worker.current_task = task.id
            
            # Preparar datos para enviar
            task_data = {
                "task_id": task.id,
                "benchmark": task.algorithm,
                "params": task.parameters
            }
            
            # Enviar tarea al worker
            url = f"http://{worker.ip}:{worker.port}/execute"
            response = requests.post(url, json=task_data, timeout=self.timeout_config['task_timeout'])
            
            if response.status_code == 200:
                # Tarea enviada exitosamente
                self.task_manager.update_task_status(task.id, TaskStatus.RUNNING)
                self.stats["tasks_distributed"] += 1
                
                logger.info(f"📤 Tarea {task.id} enviada a {worker.id}")
                
                # Procesar resultado en hilo separado
                threading.Thread(
                    target=self._process_task_result,
                    args=(task, worker, response),
                    daemon=True
                ).start()
                
            else:
                # Error enviando tarea
                self.task_manager.update_task_status(
                    task.id,
                    TaskStatus.FAILED,
                    error=f"Error HTTP {response.status_code}"
                )
                worker.current_task = None
                logger.error(f"❌ Error enviando tarea {task.id} a {worker.id}: {response.status_code}")
                
        except Exception as e:
            # Error en la comunicación
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error=str(e)
            )
            worker.current_task = None
            logger.error(f"❌ Error asignando tarea {task.id} a {worker.id}: {e}")
    
    def _process_task_result(self, task: Task, worker: WorkerStatus, response: requests.Response):
        """Procesar resultado de tarea"""
        try:
            result = response.json()
            execution_time = result.get('execution_time', 0.0)
            
            # Actualizar tarea
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.COMPLETED,
                result=result,
                execution_time=execution_time
            )
            
            # Actualizar worker
            worker.add_task_result(task.id, execution_time, True)
            worker.current_task = None
            
            # Actualizar estadísticas
            self.stats["tasks_completed"] += 1
            
            logger.info(f"✅ Tarea {task.id} completada por {worker.id} en {execution_time:.2f}s")
            
        except Exception as e:
            # Error procesando resultado
            self.task_manager.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error=f"Error procesando resultado: {str(e)}"
            )
            worker.add_task_result(task.id, 0.0, False)
            worker.current_task = None
            self.stats["tasks_failed"] += 1
            
            logger.error(f"❌ Error procesando resultado de tarea {task.id}: {e}")
    
    def _check_running_tasks(self):
        """Verificar tareas en ejecución"""
        running_tasks = [t for t in self.task_manager.tasks.values() if t.status == TaskStatus.RUNNING]
        
        for task in running_tasks:
            if task.started_at:
                # Verificar timeout
                elapsed = datetime.now() - task.started_at
                if elapsed > timedelta(seconds=self.timeout_config['task_timeout']):
                    # Tarea con timeout
                    self.task_manager.update_task_status(
                        task.id,
                        TaskStatus.FAILED,
                        error="Task timeout"
                    )
                    
                    # Liberar worker
                    if task.assigned_worker and task.assigned_worker in self.workers:
                        self.workers[task.assigned_worker].current_task = None
                    
                    logger.warning(f"⏰ Tarea {task.id} terminada por timeout")
    
    def _recover_failed_tasks(self):
        """Recuperar tareas fallidas"""
        failed_tasks = [t for t in self.task_manager.tasks.values() 
                       if t.status == TaskStatus.FAILED and t.retry_count < t.max_retries]
        
        for task in failed_tasks:
            # Incrementar contador de reintentos
            task.retry_count += 1
            
            # Volver a poner en cola
            self.task_manager.update_task_status(task.id, TaskStatus.PENDING)
            self.task_manager.pending_queue.put((-task.priority, task.id))
            
            logger.info(f"🔄 Reintentando tarea {task.id} (intento {task.retry_count}/{task.max_retries})")
    
    def _update_stats(self):
        """Actualizar estadísticas"""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        # Log periódico de estadísticas (cada 5 minutos)
        if int(uptime.total_seconds()) % 300 == 0:
            self._log_statistics()
    
    def _log_statistics(self):
        """Escribir estadísticas al log"""
        with self.worker_lock:
            active_count = len([w for w in self.workers.values() if w.status == "active"])
            healthy_count = len([w for w in self.workers.values() if w.is_healthy()])
            
            task_stats = self.task_manager.get_task_stats()
            
            success_rate = (self.stats["successful_pings"] / max(1, self.stats["total_pings"])) * 100
            
            logger.info(f"📊 Estadísticas - Workers: {active_count}/{len(self.workers)} activos, "
                       f"{healthy_count} saludables, Ping success: {success_rate:.1f}%, "
                       f"Tareas: {task_stats['completed']}/{task_stats['total_tasks']} completadas")
    
    def _save_worker_state(self):
        """Guardar estado actual de workers"""
        try:
            with self.worker_lock:
                state = {
                    "timestamp": datetime.now().isoformat(),
                    "workers": {wid: worker.to_dict() for wid, worker in self.workers.items()},
                    "stats": self.stats.copy(),
                    "task_stats": self.task_manager.get_task_stats()
                }
                
                # Convertir datetime a string para JSON
                state["stats"]["uptime_start"] = state["stats"]["uptime_start"].isoformat()
                
                with open('logs/worker_state.json', 'w') as f:
                    json.dump(state, f, indent=2)
                    
        except Exception as e:
            logger.error(f"❌ Error guardando estado: {e}")
    
    # Métodos públicos para la interfaz
    def add_task(self, algorithm: str, parameters: Dict[str, Any], priority: int = 1) -> str:
        """Agregar tarea a la cola"""
        return self.task_manager.add_task(algorithm, parameters, priority)
    
    def get_worker_status(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estado de workers"""
        with self.worker_lock:
            if worker_id:
                if worker_id in self.workers:
                    return self.workers[worker_id].to_dict()
                else:
                    return {"error": f"Worker {worker_id} no encontrado"}
            else:
                return {
                    "workers": {wid: worker.to_dict() for wid, worker in self.workers.items()},
                    "summary": {
                        "total_workers": len(self.workers),
                        "active_workers": len([w for w in self.workers.values() if w.status == "active"]),
                        "healthy_workers": len([w for w in self.workers.values() if w.is_healthy()]),
                        "available_workers": len([w for w in self.workers.values() if w.is_available()]),
                        "busy_workers": len([w for w in self.workers.values() if w.current_task])
                    }
                }
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estado de tareas"""
        if task_id:
            if task_id in self.task_manager.tasks:
                return self.task_manager.tasks[task_id].to_dict()
            else:
                return {"error": f"Tarea {task_id} no encontrada"}
        else:
            return {
                "tasks": [task.to_dict() for task in self.task_manager.tasks.values()],
                "statistics": self.task_manager.get_task_stats()
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        uptime = datetime.now() - self.stats["uptime_start"]
        task_stats = self.task_manager.get_task_stats()
        
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0],
            "ping_success_rate": (self.stats["successful_pings"] / max(1, self.stats["total_pings"])) * 100,
            "task_completion_rate": (task_stats["completed"] / max(1, task_stats["total_tasks"])) * 100,
            "task_statistics": task_stats
        }

def main():
    """Función principal"""
    print("🎭 SISTEMA DE ORQUESTACIÓN ELÁSTICO V6 - COLA DE TAREAS")
    print("=" * 70)
    print("🧠 MEMORIAS ACTIVAS:")
    print("   1. Monitor de Workers (ping constante)")
    print("   2. Monitor de Tareas (distribución automática)")
    print("=" * 70)
    
    # Crear y iniciar orquestador
    orchestrator = ElasticOrchestratorV6()
    orchestrator.start()
    
    try:
        # Interfaz interactiva
        while True:
            print("\n🎛️  MENÚ PRINCIPAL - ETAPA 6")
            print("1. Estado de workers")
            print("2. Estado de tareas")
            print("3. Agregar tarea")
            print("4. Agregar múltiples tareas")
            print("5. Estadísticas del sistema")
            print("6. Estadísticas de carga manual")
            print("7. Guardar resultados")
            print("8. Mostrar configuración")
            print("9. Salir")
            
            choice = input("\nSelecciona una opción (1-9): ").strip()
            
            if choice == "1":
                status = orchestrator.get_worker_status()
                print("\n📊 ESTADO DE WORKERS:")
                print("=" * 50)
                
                for worker_id, worker_data in status["workers"].items():
                    health_icon = "✅" if worker_data["is_healthy"] else "❌"
                    available_icon = "🟢" if worker_data["is_available"] else "🔴"
                    
                    print(f"{health_icon} {worker_id} ({worker_data['ip']}) {available_icon}")
                    print(f"   Estado: {worker_data['status']}")
                    print(f"   Tiempo respuesta: {worker_data['average_response_time']:.3f}s")
                    print(f"   Tareas completadas: {worker_data['total_tasks_completed']}")
                    print(f"   Tiempo promedio tareas: {worker_data['average_task_time']:.2f}s")
                    print(f"   Tasa de éxito: {worker_data['success_rate']:.1%}")
                    
                    if worker_data['current_task']:
                        print(f"   🔄 Ejecutando: {worker_data['current_task']}")
                    
                    print()
                
                summary = status["summary"]
                print(f"📋 RESUMEN: {summary['active_workers']}/{summary['total_workers']} activos, "
                      f"{summary['available_workers']} disponibles, {summary['busy_workers']} ocupados")
                
            elif choice == "2":
                task_status = orchestrator.get_task_status()
                print("\n📋 ESTADO DE TAREAS:")
                print("=" * 50)
                
                stats = task_status["statistics"]
                print(f"📊 Total: {stats['total_tasks']}")
                print(f"⏳ Pendientes: {stats['pending']}")
                print(f"📤 Asignadas: {stats['assigned']}")
                print(f"🔄 Ejecutando: {stats['running']}")
                print(f"✅ Completadas: {stats['completed']}")
                print(f"❌ Fallidas: {stats['failed']}")
                print(f"⏱️  Tiempo promedio: {stats['avg_execution_time']:.2f}s")
                
                # Mostrar últimas 5 tareas
                if task_status["tasks"]:
                    print("\n🔍 ÚLTIMAS 5 TAREAS:")
                    recent_tasks = sorted(task_status["tasks"], 
                                        key=lambda x: x['created_at'], reverse=True)[:5]
                    
                    for task in recent_tasks:
                        status_icon = {
                            "pending": "⏳",
                            "assigned": "📤",
                            "running": "🔄",
                            "completed": "✅",
                            "failed": "❌"
                        }.get(task["status"], "❓");
                        
                        print(f"{status_icon} {task['id'][:8]}... - {task['algorithm']}")
                        print(f"   Status: {task['status']}")
                        if task['assigned_worker']:
                            print(f"   Worker: {task['assigned_worker']}")
                        if task['execution_time']:
                            print(f"   Tiempo: {task['execution_time']:.2f}s")
                        print()
                
            elif choice == "3":
                print("\n➕ AGREGAR TAREA:")
                print("Algoritmos disponibles:")
                print("1. benchmark.py (Python puro)")
                print("2. benchmark_cython.py (Optimizado)")
                
                algo_choice = input("Selecciona algoritmo (1-2): ").strip()
                if algo_choice == "1":
                    algorithm = "benchmark.py"
                elif algo_choice == "2":
                    algorithm = "benchmark_cython.py"
                else:
                    print("❌ Opción inválida")
                    continue
                
                # Parámetros
                try:
                    particulas = int(input("Número de partículas (100): ").strip() or "100")
                    pasos = int(input("Número de pasos (500): ").strip() or "500")
                    semilla = int(input("Semilla (42): ").strip() or "42")
                    prioridad = int(input("Prioridad (1-10, mayor=más prioritaria): ").strip() or "1")
                    
                    parameters = {
                        "NUM_PARTICULAS": particulas,
                        "NUM_PASOS": pasos,
                        "SEMILLA": semilla
                    }
                    
                    task_id = orchestrator.add_task(algorithm, parameters, prioridad)
                    print(f"✅ Tarea agregada: {task_id}")
                    
                except ValueError:
                    print("❌ Parámetros inválidos")
                    
            elif choice == "4":
                print("\n➕ AGREGAR MÚLTIPLES TAREAS:")
                try:
                    cantidad = int(input("Cantidad de tareas a agregar: ").strip())
                    
                    for i in range(cantidad):
                        # Alternar entre algoritmos
                        algorithm = "benchmark.py" if i % 2 == 0 else "benchmark_cython.py"
                        
                        # Parámetros variados
                        parameters = {
                            "NUM_PARTICULAS": 100 + (i * 10),
                            "NUM_PASOS": 500 + (i * 50),
                            "SEMILLA": 42 + i
                        }
                        
                        task_id = orchestrator.add_task(algorithm, parameters)
                        print(f"✅ Tarea {i+1}/{cantidad} agregada: {task_id[:8]}...")
                        
                    print(f"🎉 {cantidad} tareas agregadas exitosamente")
                    
                except ValueError:
                    print("❌ Cantidad inválida")
                    
            elif choice == "5":
                stats = orchestrator.get_statistics()
                print("\n📈 ESTADÍSTICAS DEL SISTEMA:")
                print("=" * 50)
                print(f"⏱️  Tiempo en línea: {stats['uptime_formatted']}")
                print(f"📊 Pings totales: {stats['total_pings']}")
                print(f"📈 Tasa de éxito ping: {stats['ping_success_rate']:.1f}%")
                print(f"📤 Tareas distribuidas: {stats['tasks_distributed']}")
                print(f"✅ Tareas completadas: {stats['tasks_completed']}")
                print(f"❌ Tareas fallidas: {stats['tasks_failed']}")
                print(f"📊 Tasa de éxito tareas: {stats['task_completion_rate']:.1f}%")
                
                task_stats = stats["task_statistics"]
                print(f"⏱️  Tiempo promedio ejecución: {task_stats['avg_execution_time']:.2f}s")
                print(f"⚡ Tiempo mínimo: {task_stats['min_execution_time']:.2f}s")
                print(f"🐌 Tiempo máximo: {task_stats['max_execution_time']:.2f}s")
                
            elif choice == "6":
                auto_stats = orchestrator.get_auto_task_stats()
                print("\n🤖 ESTADÍSTICAS DE CARGA MANUAL:")
                print("=" * 50)
                print(f"📁 Archivos procesados: {auto_stats['processed_files']}")
                print(f"⏳ Archivos pendientes: {auto_stats['pending_files']}")
                print(f"📂 Directorio de colas: {auto_stats['queue_directory']}")
                print(f"� Modo: {auto_stats['mode']}")
                print(f"�🔄 Generación automática: {'Activa' if auto_stats['auto_generation_active'] else 'Desactivada'}")
                
                print(f"\n💡 INSTRUCCIONES:")
                print(f"   • Coloca archivos .json en: {auto_stats['queue_directory']}/")
                print(f"   • El sistema procesará automáticamente los nuevos archivos")
                print(f"   • Los archivos procesados se mueven a: {auto_stats['queue_directory']}/processed/")
                
                # Mostrar archivos procesados recientes
                if auto_stats['processed_files'] > 0:
                    print(f"\n📋 Últimos archivos procesados:")
                    recent_files = list(orchestrator.processed_files)[-5:]
                    for filename in recent_files:
                        print(f"   • {filename}")
                else:
                    print(f"\n📋 No hay archivos procesados aún.")
                    print(f"   Copia archivos .json a {auto_stats['queue_directory']}/ para comenzar.")
            elif choice == "7":
                orchestrator.task_manager.save_results()
                print("💾 Resultados guardados exitosamente")
                
            elif choice == "8":
                orchestrator.env_config.print_config()
                
            elif choice == "9":
                print("👋 Deteniendo orquestador...")
                orchestrator.stop()
                break
                
            else:
                print("❌ Opción inválida")
                
    except KeyboardInterrupt:
        print("\n🛑 Interrupción recibida...")
        orchestrator.stop()

if __name__ == "__main__":
    main()
