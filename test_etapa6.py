#!/usr/bin/env python3
"""
Script de pruebas para ETAPA 6
Verifica que el sistema funcione correctamente con tareas distribuidas
"""

import requests
import json
import time
import threading
from datetime import datetime
import argparse

class ETAPA6TestSuite:
    def __init__(self, orchestrator_host='localhost', orchestrator_port=5000):
        self.orchestrator_url = f"http://{orchestrator_host}:{orchestrator_port}"
        self.results = []
        
    def log(self, message, level="INFO"):
        """Logging con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_orchestrator_health(self):
        """Probar que el orchestrator está funcionando"""
        try:
            self.log("Probando salud del orchestrator...")
            response = requests.get(f"{self.orchestrator_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Orchestrator saludable")
                return True
            else:
                self.log(f"❌ Orchestrator no saludable: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error conectando al orchestrator: {e}", "ERROR")
            return False
    
    def test_worker_discovery(self):
        """Probar que el orchestrator detecta workers"""
        try:
            self.log("Probando descubrimiento de workers...")
            response = requests.get(f"{self.orchestrator_url}/workers", timeout=5)
            if response.status_code == 200:
                workers = response.json()
                if workers:
                    self.log(f"✅ {len(workers)} workers detectados")
                    for worker in workers:
                        self.log(f"   - {worker['id']}: {worker['status']}")
                    return True
                else:
                    self.log("❌ No se detectaron workers")
                    return False
            else:
                self.log(f"❌ Error obteniendo workers: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error obteniendo workers: {e}", "ERROR")
            return False
    
    def test_task_creation(self):
        """Probar creación de tareas"""
        try:
            self.log("Probando creación de tareas...")
            
            # Crear tarea de prueba
            task_data = {
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 50,
                    "NUM_PASOS": 100,
                    "SEMILLA": 42
                },
                "priority": 1
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/tasks",
                json=task_data,
                timeout=5
            )
            
            if response.status_code == 201:
                task = response.json()
                self.log(f"✅ Tarea creada: {task['id']}")
                return task['id']
            else:
                self.log(f"❌ Error creando tarea: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error creando tarea: {e}", "ERROR")
            return None
    
    def test_task_execution(self, task_id):
        """Probar ejecución de tareas"""
        try:
            self.log(f"Probando ejecución de tarea {task_id}...")
            
            # Esperar que la tarea se complete
            max_wait = 60  # 60 segundos máximo
            wait_time = 0
            
            while wait_time < max_wait:
                response = requests.get(f"{self.orchestrator_url}/tasks/{task_id}", timeout=5)
                if response.status_code == 200:
                    task = response.json()
                    status = task['status']
                    
                    if status == 'completed':
                        self.log(f"✅ Tarea completada en {task.get('execution_time', 0):.2f}s")
                        return True
                    elif status == 'failed':
                        self.log(f"❌ Tarea falló: {task.get('error', 'Unknown error')}")
                        return False
                    else:
                        self.log(f"⏳ Tarea en estado: {status}")
                        time.sleep(2)
                        wait_time += 2
                else:
                    self.log(f"❌ Error obteniendo tarea: {response.status_code}")
                    return False
            
            self.log(f"❌ Timeout esperando tarea {task_id}")
            return False
            
        except Exception as e:
            self.log(f"❌ Error ejecutando tarea: {e}", "ERROR")
            return False
    
    def test_batch_tasks(self, count=5):
        """Probar creación de múltiples tareas"""
        try:
            self.log(f"Probando creación de {count} tareas...")
            
            task_ids = []
            algorithms = ["benchmark.py", "benchmark_cython.py"]
            
            for i in range(count):
                task_data = {
                    "algorithm": algorithms[i % len(algorithms)],
                    "parameters": {
                        "NUM_PARTICULAS": 50 + (i * 10),
                        "NUM_PASOS": 100 + (i * 50),
                        "SEMILLA": 42 + i
                    },
                    "priority": 1 + (i % 3)
                }
                
                response = requests.post(
                    f"{self.orchestrator_url}/tasks",
                    json=task_data,
                    timeout=5
                )
                
                if response.status_code == 201:
                    task = response.json()
                    task_ids.append(task['id'])
                    self.log(f"✅ Tarea {i+1}/{count} creada: {task['id']}")
                else:
                    self.log(f"❌ Error creando tarea {i+1}: {response.status_code}")
            
            return task_ids
            
        except Exception as e:
            self.log(f"❌ Error creando tareas en lote: {e}", "ERROR")
            return []
    
    def test_statistics(self):
        """Probar estadísticas del sistema"""
        try:
            self.log("Probando estadísticas del sistema...")
            
            response = requests.get(f"{self.orchestrator_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log("✅ Estadísticas obtenidas:")
                self.log(f"   - Tareas totales: {stats.get('total_tasks', 0)}")
                self.log(f"   - Tareas completadas: {stats.get('completed_tasks', 0)}")
                self.log(f"   - Workers activos: {stats.get('active_workers', 0)}")
                return True
            else:
                self.log(f"❌ Error obteniendo estadísticas: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error obteniendo estadísticas: {e}", "ERROR")
            return False
    
    def test_worker_history(self, worker_host='localhost', worker_port=5001):
        """Probar historial de workers"""
        try:
            self.log(f"Probando historial de worker {worker_host}:{worker_port}...")
            
            response = requests.get(f"http://{worker_host}:{worker_port}/history", timeout=5)
            if response.status_code == 200:
                history = response.json()
                task_count = len(history.get('task_history', []))
                self.log(f"✅ Historial obtenido: {task_count} tareas")
                return True
            else:
                self.log(f"❌ Error obteniendo historial: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error obteniendo historial: {e}", "ERROR")
            return False
    
    def run_full_test_suite(self):
        """Ejecutar suite completa de pruebas"""
        self.log("🚀 INICIANDO SUITE DE PRUEBAS ETAPA 6")
        self.log("=" * 50)
        
        tests_passed = 0
        total_tests = 7
        
        # Test 1: Salud del orchestrator
        if self.test_orchestrator_health():
            tests_passed += 1
        
        # Test 2: Descubrimiento de workers
        if self.test_worker_discovery():
            tests_passed += 1
        
        # Test 3: Creación de tarea
        task_id = self.test_task_creation()
        if task_id:
            tests_passed += 1
            
            # Test 4: Ejecución de tarea
            if self.test_task_execution(task_id):
                tests_passed += 1
        
        # Test 5: Tareas en lote
        batch_tasks = self.test_batch_tasks(3)
        if batch_tasks:
            tests_passed += 1
        
        # Test 6: Estadísticas
        if self.test_statistics():
            tests_passed += 1
        
        # Test 7: Historial de worker
        if self.test_worker_history():
            tests_passed += 1
        
        # Resultados finales
        self.log("=" * 50)
        self.log(f"📊 RESULTADOS: {tests_passed}/{total_tests} pruebas pasadas")
        
        if tests_passed == total_tests:
            self.log("🎉 TODAS LAS PRUEBAS PASARON - ETAPA 6 FUNCIONANDO CORRECTAMENTE")
            return True
        else:
            self.log(f"❌ {total_tests - tests_passed} PRUEBAS FALLARON")
            return False

def main():
    parser = argparse.ArgumentParser(description='Suite de pruebas para ETAPA 6')
    parser.add_argument('--host', default='localhost', help='Host del orchestrator')
    parser.add_argument('--port', default=5000, type=int, help='Puerto del orchestrator')
    parser.add_argument('--worker-host', default='localhost', help='Host del worker para pruebas')
    parser.add_argument('--worker-port', default=5001, type=int, help='Puerto del worker para pruebas')
    parser.add_argument('--quick', action='store_true', help='Ejecutar pruebas rápidas solamente')
    
    args = parser.parse_args()
    
    # Crear suite de pruebas
    test_suite = ETAPA6TestSuite(args.host, args.port)
    
    if args.quick:
        # Pruebas rápidas
        test_suite.log("🏃 EJECUTANDO PRUEBAS RÁPIDAS")
        success = (test_suite.test_orchestrator_health() and 
                  test_suite.test_worker_discovery() and
                  test_suite.test_statistics())
        
        if success:
            test_suite.log("✅ PRUEBAS RÁPIDAS COMPLETADAS")
        else:
            test_suite.log("❌ PRUEBAS RÁPIDAS FALLARON")
    else:
        # Suite completa
        success = test_suite.run_full_test_suite()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
