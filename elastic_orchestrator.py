#!/usr/bin/env python3
"""
ETAPA 5: SISTEMA DE ORQUESTACIÓN ELÁSTICO
=========================================

Implementa un maestro elástico con 2 memorias (hilos) que monitorean constantemente:
1. MEMORIA 1: Monitor de Workers (ping constante)
2. MEMORIA 2: Monitor de Tareas (preparación para ETAPA 6)

Características:
- Monitoreo continuo de workers
- Detección automática de workers que se conectan/desconectan
- Estado persistente de workers
- Interfaz de gestión en tiempo real
- Logs detallados
- Recuperación automática de fallos
"""

import requests
import json
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config_manager import get_config
import signal
import sys
from dataclasses import dataclass
from collections import deque
import queue

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
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = deque(maxlen=10)  # Últimos 10 tiempos de respuesta
    
    def update_response_time(self, response_time: float):
        """Actualizar tiempo de respuesta"""
        self.response_times.append(response_time)
        self.average_response_time = sum(self.response_times) / len(self.response_times)
    
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
            "is_healthy": self.is_healthy()
        }

class ElasticOrchestrator:
    """Orquestador elástico con monitoreo continuo"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Inicializar el orquestador elástico"""
        self.env_config = get_config()
        self.running = False
        self.workers: Dict[str, WorkerStatus] = {}
        self.worker_lock = threading.RLock()
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Configuración desde .env
        self.docker_config = self.env_config.get_docker_config()
        self.timeout_config = self.env_config.get_timeout_config()
        self.benchmark_config = self.env_config.get_benchmark_config()
        
        # Configuración de monitoreo
        self.ping_interval = 5  # segundos entre pings
        self.health_check_interval = 10  # segundos entre verificaciones de salud
        self.max_ping_failures = 5
        
        # Cargar workers desde configuración
        self._load_workers_config(config_file)
        
        # Hilos de monitoreo
        self.worker_monitor_thread = None
        self.task_monitor_thread = None
        
        # Estadísticas
        self.stats = {
            "total_pings": 0,
            "successful_pings": 0,
            "failed_pings": 0,
            "workers_discovered": 0,
            "workers_lost": 0,
            "uptime_start": datetime.now()
        }
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 Orquestador elástico inicializado")
    
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
            self.workers[worker_id] = WorkerStatus(
                id=worker_id,
                ip=worker_data['ip'],
                port=worker_data['port']
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
        logger.info("🎯 Iniciando orquestador elástico...")
        
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
        
        # Iniciar MEMORIA 2: Monitor de Tareas (preparación para ETAPA 6)
        self.task_monitor_thread = threading.Thread(
            target=self._task_monitor_loop,
            name="TaskMonitor",
            daemon=True
        )
        self.task_monitor_thread.start()
        logger.info("🧠 MEMORIA 2: Monitor de Tareas iniciado")
        
        logger.info("✅ Orquestador elástico iniciado exitosamente")
    
    def stop(self):
        """Detener el orquestador elástico"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador elástico...")
        self.running = False
        
        # Esperar a que terminen los hilos
        if self.worker_monitor_thread and self.worker_monitor_thread.is_alive():
            self.worker_monitor_thread.join(timeout=5)
        
        if self.task_monitor_thread and self.task_monitor_thread.is_alive():
            self.task_monitor_thread.join(timeout=5)
        
        logger.info("✅ Orquestador elástico detenido")
    
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
        """MEMORIA 2: Loop principal del monitor de tareas (preparación ETAPA 6)"""
        logger.info("🔄 Iniciando loop de monitoreo de tareas...")
        
        while self.running:
            try:
                # Por ahora, solo logging y preparación para ETAPA 6
                # En ETAPA 6 se implementará la gestión de cola de tareas
                
                # Verificar cola de tareas
                if not self.task_queue.empty():
                    logger.info(f"📋 Tareas en cola: {self.task_queue.qsize()}")
                
                # Verificar resultados
                if not self.result_queue.empty():
                    logger.info(f"📊 Resultados pendientes: {self.result_queue.qsize()}")
                
                # Simular preparación para gestión de tareas
                self._prepare_task_management()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en monitor de tareas: {e}")
                time.sleep(1)
    
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
                worker.status = "active"
                worker.last_ping = datetime.now()
                worker.last_successful_ping = datetime.now()
                worker.consecutive_failures = 0
                worker.update_response_time(response_time)
                
                self.stats["successful_pings"] += 1
                
                if self.env_config.is_verbose():
                    logger.debug(f"✅ Ping exitoso a {worker.id} ({response_time:.3f}s)")
                
                # Verificar si es un worker recién conectado
                if worker.status == "unknown":
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
            worker.status = "inactive"
        else:
            worker.status = "unstable"
        
        if self.env_config.is_verbose():
            logger.debug(f"❌ Ping fallido a {worker.id}: {error} (fallos: {worker.consecutive_failures})")
    
    def _check_worker_health(self):
        """Verificar salud general de workers"""
        with self.worker_lock:
            active_workers = [w for w in self.workers.values() if w.status == "active"]
            healthy_workers = [w for w in self.workers.values() if w.is_healthy()]
            
            if len(active_workers) != len(healthy_workers):
                logger.warning(f"⚠️  {len(active_workers)} workers activos, {len(healthy_workers)} saludables")
    
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
            
            success_rate = (self.stats["successful_pings"] / max(1, self.stats["total_pings"])) * 100
            
            logger.info(f"📊 Estadísticas - Workers: {active_count}/{len(self.workers)} activos, "
                       f"{healthy_count} saludables, Ping success: {success_rate:.1f}%")
    
    def _save_worker_state(self):
        """Guardar estado actual de workers"""
        try:
            with self.worker_lock:
                state = {
                    "timestamp": datetime.now().isoformat(),
                    "workers": {wid: worker.to_dict() for wid, worker in self.workers.items()},
                    "stats": self.stats.copy()
                }
                
                # Convertir datetime a string para JSON
                state["stats"]["uptime_start"] = state["stats"]["uptime_start"].isoformat()
                
                with open('logs/worker_state.json', 'w') as f:
                    json.dump(state, f, indent=2)
                    
        except Exception as e:
            logger.error(f"❌ Error guardando estado: {e}")
    
    def _prepare_task_management(self):
        """Preparar gestión de tareas para ETAPA 6"""
        # Placeholder para funcionalidad futura
        # En ETAPA 6 se implementará:
        # - Distribución automática de tareas
        # - Balanceamiento de carga
        # - Recuperación de tareas fallidas
        # - Priorización de tareas
        pass
    
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
                        "inactive_workers": len([w for w in self.workers.values() if w.status == "inactive"])
                    }
                }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        uptime = datetime.now() - self.stats["uptime_start"]
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0],  # Sin microsegundos
            "ping_success_rate": (self.stats["successful_pings"] / max(1, self.stats["total_pings"])) * 100
        }
    
    def execute_task(self, task: Dict[str, Any], worker_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Ejecutar una tarea en un worker específico o automáticamente"""
        if worker_id:
            # Ejecutar en worker específico
            if worker_id not in self.workers:
                return {"error": f"Worker {worker_id} no encontrado"}
            
            worker = self.workers[worker_id]
            if not worker.is_healthy():
                return {"error": f"Worker {worker_id} no está saludable"}
            
            return self._execute_task_on_worker(worker, task)
        else:
            # Ejecutar automáticamente en el mejor worker disponible
            best_worker = self._find_best_worker()
            if not best_worker:
                return {"error": "No hay workers disponibles"}
            
            return self._execute_task_on_worker(best_worker, task)
    
    def _find_best_worker(self) -> Optional[WorkerStatus]:
        """Encontrar el mejor worker disponible"""
        with self.worker_lock:
            healthy_workers = [w for w in self.workers.values() if w.is_healthy()]
            
            if not healthy_workers:
                return None
            
            # Ordenar por tiempo de respuesta promedio
            healthy_workers.sort(key=lambda w: w.average_response_time)
            return healthy_workers[0]
    
    def _execute_task_on_worker(self, worker: WorkerStatus, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ejecutar tarea en un worker específico"""
        try:
            url = f"http://{worker.ip}:{worker.port}/execute"
            
            logger.info(f"🚀 Ejecutando tarea en {worker.id}")
            
            response = requests.post(url, json=task, timeout=self.timeout_config['task_timeout'])
            
            if response.status_code == 200:
                result = response.json()
                worker.total_tasks_completed += 1
                
                logger.info(f"✅ Tarea completada en {worker.id}")
                return result
            else:
                logger.error(f"❌ Error ejecutando tarea en {worker.id}: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando tarea en {worker.id}: {e}")
            return {"error": str(e)}

def main():
    """Función principal"""
    print("🎭 SISTEMA DE ORQUESTACIÓN ELÁSTICO - ETAPA 5")
    print("=" * 60)
    print("🧠 MEMORIAS ACTIVAS:")
    print("   1. Monitor de Workers (ping constante)")
    print("   2. Monitor de Tareas (preparación ETAPA 6)")
    print("=" * 60)
    
    # Crear y iniciar orquestador
    orchestrator = ElasticOrchestrator()
    orchestrator.start()
    
    try:
        # Interfaz interactiva
        while True:
            print("\n🎛️  MENÚ PRINCIPAL")
            print("1. Estado de workers")
            print("2. Estadísticas del sistema")
            print("3. Ejecutar tarea")
            print("4. Mostrar configuración")
            print("5. Logs en tiempo real")
            print("6. Salir")
            
            choice = input("\nSelecciona una opción (1-6): ").strip()
            
            if choice == "1":
                status = orchestrator.get_worker_status()
                print("\n📊 ESTADO DE WORKERS:")
                print("=" * 40)
                
                for worker_id, worker_data in status["workers"].items():
                    health_icon = "✅" if worker_data["is_healthy"] else "❌"
                    print(f"{health_icon} {worker_id} ({worker_data['ip']})")
                    print(f"   Estado: {worker_data['status']}")
                    print(f"   Tiempo respuesta: {worker_data['average_response_time']:.3f}s")
                    print(f"   Tareas completadas: {worker_data['total_tasks_completed']}")
                    print(f"   Último ping: {worker_data['last_ping']}")
                    print()
                
                summary = status["summary"]
                print(f"📋 RESUMEN: {summary['active_workers']}/{summary['total_workers']} activos, "
                      f"{summary['healthy_workers']} saludables")
                
            elif choice == "2":
                stats = orchestrator.get_statistics()
                print("\n📈 ESTADÍSTICAS DEL SISTEMA:")
                print("=" * 40)
                print(f"⏱️  Tiempo en línea: {stats['uptime_formatted']}")
                print(f"📊 Pings totales: {stats['total_pings']}")
                print(f"✅ Pings exitosos: {stats['successful_pings']}")
                print(f"❌ Pings fallidos: {stats['failed_pings']}")
                print(f"📈 Tasa de éxito: {stats['ping_success_rate']:.1f}%")
                print(f"🔗 Workers descubiertos: {stats['workers_discovered']}")
                print(f"💔 Workers perdidos: {stats['workers_lost']}")
                
            elif choice == "3":
                status = orchestrator.get_worker_status()
                healthy_workers = [w for w in status["workers"].values() if w["is_healthy"]]
                
                if not healthy_workers:
                    print("❌ No hay workers saludables disponibles")
                    continue
                
                print("\n🎯 EJECUTAR TAREA:")
                print("Workers disponibles:")
                for i, worker in enumerate(healthy_workers):
                    print(f"{i+1}. {worker['id']} ({worker['ip']}) - {worker['average_response_time']:.3f}s")
                print(f"{len(healthy_workers)+1}. Automático (mejor worker)")
                
                try:
                    worker_choice = input("Selecciona worker: ").strip()
                    
                    if worker_choice == str(len(healthy_workers)+1):
                        selected_worker_id = None
                    else:
                        worker_idx = int(worker_choice) - 1
                        selected_worker_id = healthy_workers[worker_idx]["id"]
                    
                    # Configurar tarea
                    print("\nConfigurar tarea:")
                    benchmark = input("Benchmark (benchmark.py/benchmark_cython.py): ").strip() or "benchmark.py"
                    particulas = input("Partículas (100): ").strip() or "100"
                    pasos = input("Pasos (500): ").strip() or "500"
                    semilla = input("Semilla (42): ").strip() or "42"
                    
                    task = {
                        "benchmark": benchmark,
                        "params": {
                            "NUM_PARTICULAS": int(particulas),
                            "NUM_PASOS": int(pasos),
                            "SEMILLA": int(semilla)
                        }
                    }
                    
                    result = orchestrator.execute_task(task, selected_worker_id)
                    
                    if result and "error" not in result:
                        print("✅ Tarea ejecutada exitosamente")
                        print(f"   Tiempo: {result.get('execution_time', 'N/A')}s")
                    else:
                        print(f"❌ Error: {result.get('error', 'Desconocido')}")
                        
                except (ValueError, IndexError):
                    print("❌ Selección inválida")
                    
            elif choice == "4":
                orchestrator.env_config.print_config()
                
            elif choice == "5":
                print("\n📋 LOGS EN TIEMPO REAL (Ctrl+C para salir):")
                print("=" * 40)
                try:
                    # Mostrar logs en tiempo real
                    import subprocess
                    subprocess.run(["tail", "-f", "logs/elastic_orchestrator.log"])
                except KeyboardInterrupt:
                    print("\n↩️  Volviendo al menú...")
                except FileNotFoundError:
                    print("❌ No se encontró el archivo de logs")
                    
            elif choice == "6":
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
