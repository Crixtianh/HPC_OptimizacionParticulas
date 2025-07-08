import requests
import json
import time
import threading
from datetime import datetime
import os
from config_manager import get_config

class Orchestrator:
    def __init__(self, config_file=None):
        # Cargar configuración desde .env
        self.env_config = get_config()
        
        # Si se especifica un archivo JSON, usarlo como respaldo
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                json_config = json.load(f)
            self.workers = json_config['workers']
            self.timeout = json_config['orchestrator']['timeout']
            self.retry_attempts = json_config['orchestrator']['retry_attempts']
        else:
            # Usar configuración desde .env
            workers_config = self.env_config.get_workers_config()
            self.workers = workers_config['workers']
            self.timeout = workers_config['orchestrator']['timeout']
            self.retry_attempts = workers_config['orchestrator']['retry_attempts']
        
        # Configuración adicional desde .env
        self.docker_config = self.env_config.get_docker_config()
        self.timeout_config = self.env_config.get_timeout_config()
        self.benchmark_config = self.env_config.get_benchmark_config()
        self.default_params = self.env_config.get_default_simulation_params()
        
        # Usar timeouts desde .env
        self.http_timeout = self.timeout_config['http_timeout']
        self.task_timeout = self.timeout_config['task_timeout']
        
    def ping_worker(self, worker):
        """Ping a un worker específico"""
        try:
            url = f"http://{worker['ip']}:{worker['port']}/ping"
            response = requests.get(url, timeout=self.http_timeout)
            
            if response.status_code == 200:
                data = response.json()
                worker['status'] = 'active'
                worker['last_ping'] = datetime.now().isoformat()
                
                if self.env_config.is_verbose():
                    print(f"✅ {worker['id']} ({worker['ip']}) - ACTIVO")
                    print(f"   Worker ID: {data.get('worker_id', 'unknown')}")
                return True
            else:
                worker['status'] = 'error'
                print(f"❌ {worker['id']} ({worker['ip']}) - ERROR: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            worker['status'] = 'inactive'
            print(f"❌ {worker['id']} ({worker['ip']}) - No se puede conectar (VM apagada)")
            return False
        except requests.exceptions.Timeout:
            worker['status'] = 'timeout'
            print(f"❌ {worker['id']} ({worker['ip']}) - Timeout")
            return False
        except Exception as e:
            worker['status'] = 'error'
            print(f"❌ {worker['id']} ({worker['ip']}) - Error: {str(e)}")
            return False
    
    def ping_all_workers(self):
        """Ping a todos los workers"""
        print("🔍 Verificando estado de workers...")
        print("=" * 50)
        active_workers = []
        
        for worker in self.workers:
            if self.ping_worker(worker):
                active_workers.append(worker)
        
        print("=" * 50)
        if not active_workers:
            print("⚠️  NO HAY MÁQUINAS ACTIVAS")
            print("   Verifica que las VMs estén encendidas y ejecutando worker_service.py")
            print("   Comando en cada VM: python3 worker_service.py")
        else:
            print(f"✅ {len(active_workers)} máquinas activas de {len(self.workers)} total")
        
        return active_workers
    
    def execute_task(self, worker, task):
        """Ejecutar tarea en un worker específico"""
        try:
            url = f"http://{worker['ip']}:{worker['port']}/execute"
            
            if self.env_config.is_verbose():
                print(f"🚀 Enviando tarea a {worker['id']} ({worker['ip']})...")
            
            response = requests.post(url, json=task, timeout=self.task_timeout)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Tarea completada en {worker['id']}")
                
                if self.env_config.is_verbose():
                    print(f"   Tiempo: {result.get('execution_time', 'N/A')} segundos")
                    print(f"   Colisiones P-P: {result.get('particle_collisions', 'N/A')}")
                    print(f"   Colisiones Pared: {result.get('wall_collisions', 'N/A')}")
                return result
            else:
                print(f"❌ Error en {worker['id']}: {response.status_code}")
                if response.text and self.env_config.is_debug_mode():
                    print(f"   Detalle: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ No se puede conectar a {worker['id']}")
            return None
        except requests.exceptions.Timeout:
            print(f"❌ Timeout ejecutando en {worker['id']}")
            return None
        except Exception as e:
            print(f"❌ Error ejecutando en {worker['id']}: {str(e)}")
            return None
    
    def get_worker_status(self, worker):
        """Obtener estado detallado de un worker"""
        try:
            url = f"http://{worker['ip']}:{worker['port']}/status"
            response = requests.get(url, timeout=self.http_timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.Timeout:
            return None
        except Exception as e:
            if self.env_config.is_debug_mode():
                print(f"🐛 Debug - Error obteniendo status de {worker['id']}: {str(e)}")
            return None
    
    def run_demo(self):
        """Ejecutar demo completo del sistema"""
        print("🎭 DEMO DEL SISTEMA DE ORQUESTACIÓN")
        print("=" * 60)
        
        # Mostrar configuración actual
        if self.env_config.is_verbose():
            print("\n🔧 Configuración actual:")
            print(f"   - Docker: {self.docker_config['full_image']}")
            print(f"   - Timeouts: HTTP={self.http_timeout}s, Task={self.task_timeout}s")
            print(f"   - Workers configurados: {len(self.workers)}")
            print("=" * 60)
        
        # 1. Verificar workers
        active_workers = self.ping_all_workers()
        
        if not active_workers:
            return
        
        print("\n" + "=" * 60)
        print("📊 ESTADO DETALLADO DE WORKERS")
        print("=" * 60)
        
        # 2. Obtener estado detallado
        for worker in active_workers:
            status = self.get_worker_status(worker)
            if status:
                print(f"\n🖥️  {worker['id']} ({worker['ip']}):")
                print(f"   Docker disponible: {status.get('docker_available', 'N/A')}")
                print(f"   Imagen disponible: {status.get('image_available', 'N/A')}")
                if self.env_config.is_verbose():
                    print(f"   Timestamp: {status.get('timestamp', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🧪 EJECUTANDO TAREAS DE PRUEBA")
        print("=" * 60)
        
        # 3. Ejecutar tareas de prueba usando configuración desde .env
        default_params = self.default_params
        test_tasks = [
            {
                "benchmark": self.benchmark_config['python'],
                "params": {
                    "NUM_PARTICULAS": default_params['num_particles'],
                    "NUM_PASOS": default_params['num_steps'],
                    "SEMILLA": default_params['seed']
                }
            },
            {
                "benchmark": self.benchmark_config['cython'],
                "params": {
                    "NUM_PARTICULAS": default_params['num_particles'],
                    "NUM_PASOS": default_params['num_steps'],
                    "SEMILLA": default_params['seed']
                }
            }
        ]
        
        for i, task in enumerate(test_tasks):
            if i < len(active_workers):
                worker = active_workers[i]
                print(f"\n📋 Tarea {i+1}: {task['benchmark']}")
                result = self.execute_task(worker, task)
                
                if result:
                    print("   ✅ Tarea completada exitosamente")
                else:
                    print("   ❌ Tarea falló")
            else:
                print(f"\n⏭️  Saltando tarea {i+1} - No hay workers disponibles")
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETADO")
        print("=" * 60)

def main():
    print("🎛️  SISTEMA DE ORQUESTACIÓN CON CONFIGURACIÓN .ENV")
    print("=" * 60)
    
    orch = Orchestrator()
    
    # Mostrar configuración al inicio si está en modo verbose
    if orch.env_config.is_verbose():
        orch.env_config.print_config()
    
    while True:
        print("\n🎛️  MENÚ PRINCIPAL")
        print("1. Verificar workers")
        print("2. Ejecutar tarea específica")
        print("3. Demo completo")
        print("4. Mostrar configuración")
        print("5. Recargar configuración")
        print("6. Salir")
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
        if choice == "1":
            orch.ping_all_workers()
            
        elif choice == "2":
            active_workers = orch.ping_all_workers()
            if not active_workers:
                continue
                
            print("\nWorkers disponibles:")
            for i, worker in enumerate(active_workers):
                print(f"{i+1}. {worker['id']} ({worker['ip']})")
            
            try:
                worker_idx = int(input("Selecciona worker (número): ")) - 1
                if 0 <= worker_idx < len(active_workers):
                    selected_worker = active_workers[worker_idx]
                    
                    print("\nBenchmarks disponibles:")
                    print(f"1. {orch.benchmark_config['python']} (Python puro)")
                    print(f"2. {orch.benchmark_config['cython']} (Optimizado)")
                    
                    benchmark_choice = input("Selecciona benchmark (1-2): ").strip()
                    benchmark = orch.benchmark_config['python'] if benchmark_choice == "1" else orch.benchmark_config['cython']
                    
                    # Usar valores por defecto desde .env
                    default_params = orch.default_params
                    print(f"\nValores por defecto desde .env:")
                    print(f"  - Partículas: {default_params['num_particles']}")
                    print(f"  - Pasos: {default_params['num_steps']}")
                    print(f"  - Semilla: {default_params['seed']}")
                    
                    use_defaults = input("¿Usar valores por defecto? (Y/n): ").strip().lower()
                    
                    if use_defaults == '' or use_defaults == 'y':
                        particulas = default_params['num_particles']
                        pasos = default_params['num_steps']
                        semilla = default_params['seed']
                    else:
                        particulas = int(input("Número de partículas: "))
                        pasos = int(input("Número de pasos: "))
                        semilla = int(input("Semilla: "))
                    
                    task = {
                        "benchmark": benchmark,
                        "params": {
                            "NUM_PARTICULAS": particulas,
                            "NUM_PASOS": pasos,
                            "SEMILLA": semilla
                        }
                    }
                    
                    orch.execute_task(selected_worker, task)
                else:
                    print("❌ Worker inválido")
                    
            except ValueError:
                print("❌ Entrada inválida")
                
        elif choice == "3":
            orch.run_demo()
        
        elif choice == "4":
            orch.env_config.print_config()
        
        elif choice == "5":
            print("🔄 Recargando configuración...")
            from config_manager import reload_config
            reload_config()
            orch = Orchestrator()
            print("✅ Configuración recargada")
            
        elif choice == "6":
            print("👋 Saliendo del orquestador...")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
