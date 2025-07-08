import requests
import json
import time

# Configuración de workers
WORKERS = [
    {"id": "worker-01", "ip": "192.168.1.93", "port": 8080},
    {"id": "worker-02", "ip": "172.20.10.9", "port": 8080}
]

def test_worker_ping(worker):
    """Probar ping a un worker"""
    try:
        url = f"http://{worker['ip']}:{worker['port']}/ping"
        print(f"🔍 Probando ping: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {worker['id']} responde correctamente")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Worker ID: {data.get('worker_id', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"❌ {worker['id']} error HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {worker['id']} - No se puede conectar (VM apagada o servicio no iniciado)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {worker['id']} - Timeout (servicio muy lento o bloqueado)")
        return False
    except Exception as e:
        print(f"❌ {worker['id']} - Error inesperado: {str(e)}")
        return False

def test_worker_status(worker):
    """Probar endpoint de status detallado"""
    try:
        url = f"http://{worker['ip']}:{worker['port']}/status"
        print(f"📊 Probando status: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {worker['id']} status detallado:")
            print(f"   Docker disponible: {data.get('docker_available', 'N/A')}")
            print(f"   Imagen particle-simulation: {data.get('image_available', 'N/A')}")
            print(f"   Worker ID: {data.get('worker_id', 'N/A')}")
            
            if not data.get('docker_available', False):
                print("   ⚠️  Docker no está funcionando en esta VM")
            if not data.get('image_available', False):
                print("   ⚠️  Imagen particle-simulation no encontrada")
                
            return True
        else:
            print(f"❌ {worker['id']} error en status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {worker['id']} - No se puede conectar (VM apagada o servicio no iniciado)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {worker['id']} - Timeout en status")
        return False
    except Exception as e:
        print(f"❌ {worker['id']} error en status: {str(e)}")
        return False

def test_worker_execution(worker):
    """Probar ejecución de tarea en worker"""
    try:
        url = f"http://{worker['ip']}:{worker['port']}/execute"
        task = {
            "benchmark": "benchmark.py",
            "params": {
                "NUM_PARTICULAS": 25,
                "NUM_PASOS": 50,
                "SEMILLA": 123
            }
        }
        
        print(f"🚀 Enviando tarea de prueba a {worker['id']}...")
        print(f"   Parámetros: {task['params']}")
        
        start_time = time.time()
        response = requests.post(url, json=task, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {worker['id']} completó tarea en {end_time - start_time:.2f}s")
            print(f"   Tiempo ejecución: {result.get('execution_time', 'N/A')}s")
            print(f"   Colisiones P-P: {result.get('particle_collisions', 'N/A')}")
            print(f"   Colisiones Pared: {result.get('wall_collisions', 'N/A')}")
            print(f"   Worker ID: {result.get('worker_id', 'N/A')}")
            return True
        else:
            print(f"❌ {worker['id']} error ejecutando: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Desconocido')}")
            except:
                print(f"   Respuesta: {response.text[:100]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {worker['id']} - No se puede conectar (VM apagada o servicio no iniciado)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {worker['id']} - Timeout en ejecución (>60s)")
        return False
    except Exception as e:
        print(f"❌ {worker['id']} error en ejecución: {str(e)}")
        return False

def test_worker_cython_execution(worker):
    """Probar ejecución de benchmark Cython"""
    try:
        url = f"http://{worker['ip']}:{worker['port']}/execute"
        task = {
            "benchmark": "benchmark_cython.py",
            "params": {
                "NUM_PARTICULAS": 25,
                "NUM_PASOS": 50,
                "SEMILLA": 123
            }
        }
        
        print(f"🔥 Probando benchmark Cython en {worker['id']}...")
        
        start_time = time.time()
        response = requests.post(url, json=task, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {worker['id']} completó Cython en {end_time - start_time:.2f}s")
            print(f"   Tiempo ejecución: {result.get('execution_time', 'N/A')}s")
            print(f"   Colisiones P-P: {result.get('particle_collisions', 'N/A')}")
            print(f"   Colisiones Pared: {result.get('wall_collisions', 'N/A')}")
            return True
        else:
            print(f"❌ {worker['id']} error en Cython: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Desconocido')}")
            except:
                pass
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {worker['id']} - No se puede conectar para Cython")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {worker['id']} - Timeout en Cython (>60s)")
        return False
    except Exception as e:
        print(f"❌ {worker['id']} error en Cython: {str(e)}")
        return False

def run_full_test():
    """Ejecutar suite completa de pruebas"""
    print("🧪 SUITE COMPLETA DE PRUEBAS DE COMUNICACIÓN")
    print("=" * 60)
    
    active_workers = []
    
    for worker in WORKERS:
        print(f"\n🖥️  PROBANDO {worker['id']} ({worker['ip']})")
        print("-" * 40)
        
        # Test 1: Ping básico
        if test_worker_ping(worker):
            # Test 2: Status detallado
            if test_worker_status(worker):
                # Test 3: Ejecución Python
                if test_worker_execution(worker):
                    # Test 4: Ejecución Cython
                    test_worker_cython_execution(worker)
                    active_workers.append(worker)
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    print(f"✅ Workers activos: {len(active_workers)}/{len(WORKERS)}")
    
    if active_workers:
        print("🔗 Workers funcionando:")
        for worker in active_workers:
            print(f"   - {worker['id']} ({worker['ip']})")
        
        print("\n🚀 El sistema está listo para orquestación!")
        print("   Ejecuta: python orchestrator.py")
    else:
        print("❌ No hay workers activos.")
        print("\n🔧 Para solucionar:")
        print("   1. Verifica que las VMs estén encendidas")
        print("   2. En cada VM, ejecuta: python3 worker_service.py")
        print("   3. Verifica que Docker esté instalado y funcionando")
        print("   4. Verifica la imagen: docker images particle-simulation")

def main():
    print("🔧 HERRAMIENTA DE PRUEBAS DE COMUNICACIÓN")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Ping rápido a todos los workers")
        print("2. Suite completa de pruebas")
        print("3. Probar worker específico")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            print("\n🔍 PING RÁPIDO")
            print("-" * 30)
            for worker in WORKERS:
                test_worker_ping(worker)
                
        elif choice == "2":
            run_full_test()
            
        elif choice == "3":
            print("\nWorkers disponibles:")
            for i, worker in enumerate(WORKERS):
                print(f"{i+1}. {worker['id']} ({worker['ip']})")
            
            try:
                idx = int(input("Selecciona worker (número): ")) - 1
                if 0 <= idx < len(WORKERS):
                    worker = WORKERS[idx]
                    print(f"\n🔍 Probando {worker['id']}...")
                    
                    if test_worker_ping(worker):
                        test_worker_status(worker)
                        test_worker_execution(worker)
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Entrada inválida")
                
        elif choice == "4":
            print("👋 Saliendo...")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
