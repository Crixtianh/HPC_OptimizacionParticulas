from flask import Flask, request, jsonify
import subprocess
import json
import time
import os
import socket
from datetime import datetime
import threading

# Importar configuración desde .env
try:
    from config_manager import get_config
    env_config = get_config()
    USE_ENV_CONFIG = True
except ImportError:
    USE_ENV_CONFIG = False
    env_config = None

app = Flask(__name__)

# Configuración global
WORKER_ID = os.getenv('WORKER_ID', 'worker-unknown')

# Obtener configuración desde .env si está disponible
if USE_ENV_CONFIG:
    docker_config = env_config.get_docker_config()
    DOCKER_IMAGE = docker_config['full_image']
    BENCHMARK_PYTHON = env_config.get_benchmark_config()['python']
    BENCHMARK_CYTHON = env_config.get_benchmark_config()['cython']
    DEBUG_MODE = env_config.is_debug_mode()
    VERBOSE_MODE = env_config.is_verbose()
else:
    # Valores por defecto si no hay .env
    DOCKER_IMAGE = "particle-simulation:latest"
    BENCHMARK_PYTHON = "benchmark.py"
    BENCHMARK_CYTHON = "benchmark_cython.py"
    DEBUG_MODE = False
    VERBOSE_MODE = True

# Variables para almacenar histórico de tareas (ETAPA 6)
task_history = []
task_history_lock = threading.Lock()
current_task = None
current_task_lock = threading.Lock()

def log_message(message, level="INFO"):
    """Función para logging con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if VERBOSE_MODE:
        print(f"[{timestamp}] [{level}] {message}")

def save_task_result(task_id, algorithm, parameters, execution_time, success, result=None, error=None):
    """Guardar resultado de tarea en histórico (ETAPA 6)"""
    with task_history_lock:
        task_result = {
            "task_id": task_id,
            "algorithm": algorithm,
            "parameters": parameters,
            "execution_time": execution_time,
            "success": success,
            "result": result,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "worker_id": WORKER_ID
        }
        
        task_history.append(task_result)
        
        # Mantener solo los últimos 100 resultados
        if len(task_history) > 100:
            task_history.pop(0)
        
        # Guardar en archivo JSON
        try:
            os.makedirs('results', exist_ok=True)
            with open(f'results/worker_{WORKER_ID}_history.json', 'w') as f:
                json.dump(task_history, f, indent=2)
        except Exception as e:
            log_message(f"Error guardando histórico: {e}", "ERROR")

def get_task_statistics():
    """Obtener estadísticas de tareas ejecutadas"""
    with task_history_lock:
        if not task_history:
            return {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "min_execution_time": 0.0,
                "max_execution_time": 0.0
            }
        
        total_tasks = len(task_history)
        successful_tasks = sum(1 for task in task_history if task["success"])
        failed_tasks = total_tasks - successful_tasks
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
        
        execution_times = [task["execution_time"] for task in task_history if task["success"]]
        
        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
            min_execution_time = min(execution_times)
            max_execution_time = max(execution_times)
        else:
            avg_execution_time = 0.0
            min_execution_time = 0.0
            max_execution_time = 0.0
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "min_execution_time": min_execution_time,
            "max_execution_time": max_execution_time
        }

@app.route('/ping', methods=['GET'])
def ping():
    """Endpoint para verificar que el worker está activo"""
    log_message(f"Ping recibido desde {request.remote_addr}")
    
    # Incluir información de tarea actual (ETAPA 6)
    with current_task_lock:
        current_task_info = current_task.copy() if current_task else None
    
    return jsonify({
        "status": "active",
        "worker_id": WORKER_ID,
        "timestamp": datetime.now().isoformat(),
        "current_task": current_task_info,
        "docker_available": check_docker_availability(),
        "task_statistics": get_task_statistics(),
        "message": "Worker is running and ready",
        "config": {
            "docker_image": DOCKER_IMAGE,
            "debug_mode": DEBUG_MODE,
            "using_env_config": USE_ENV_CONFIG
        }
    })

@app.route('/execute', methods=['POST'])
def execute_task():
    """Endpoint para ejecutar una tarea (benchmark) - ETAPA 6"""
    try:
        task_data = request.get_json()
        
        if not task_data:
            log_message("Error: No se recibió task_data", "ERROR")
            return jsonify({"error": "No task data provided"}), 400
        
        # Obtener parámetros de la tarea (ETAPA 6)
        task_id = task_data.get('task_id', 'unknown')
        benchmark = task_data.get('benchmark', BENCHMARK_PYTHON)
        params = task_data.get('params', {})
        
        num_particulas = params.get('NUM_PARTICULAS', 100)
        num_pasos = params.get('NUM_PASOS', 500)
        semilla = params.get('SEMILLA', 42)
        
        log_message(f"Ejecutando tarea {task_id}: {benchmark} con {num_particulas} partículas, {num_pasos} pasos, semilla {semilla}")
        
        # Marcar tarea actual (ETAPA 6)
        with current_task_lock:
            global current_task
            current_task = {
                "task_id": task_id,
                "benchmark": benchmark,
                "params": params,
                "started_at": datetime.now().isoformat()
            }
        
        # Construir comando Docker usando configuración
        if benchmark == BENCHMARK_CYTHON:
            cmd = [
                'docker', 'run', '--rm', DOCKER_IMAGE,
                'python', BENCHMARK_CYTHON,
                str(num_particulas), str(num_pasos), str(semilla)
            ]
        else:
            cmd = [
                'docker', 'run', '--rm', DOCKER_IMAGE,
                'python', BENCHMARK_PYTHON,
                str(num_particulas), str(num_pasos), str(semilla)
            ]
        
        if DEBUG_MODE:
            log_message(f"Comando a ejecutar: {' '.join(cmd)}", "DEBUG")
        
        # Ejecutar tarea
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        execution_time = time.time() - start_time
        
        # Limpiar tarea actual
        with current_task_lock:
            current_task = None
        
        if result.returncode == 0:
            log_message(f"Tarea {task_id} completada exitosamente en {execution_time:.2f} segundos")
            
            # Parsear resultados
            try:
                output_lines = result.stdout.strip().split('\n')
                particle_collisions = None
                wall_collisions = None
                
                for line in output_lines:
                    if 'Colisiones partícula-partícula:' in line:
                        particle_collisions = int(line.split(':')[1].strip())
                    elif 'Colisiones con paredes:' in line:
                        wall_collisions = int(line.split(':')[1].strip())
                
                # Preparar resultado
                task_result = {
                    "status": "success",
                    "execution_time": execution_time,
                    "particle_collisions": particle_collisions,
                    "wall_collisions": wall_collisions,
                    "worker_id": WORKER_ID,
                    "timestamp": datetime.now().isoformat(),
                    "benchmark": benchmark,
                    "params": params,
                    "full_output": result.stdout if DEBUG_MODE else None
                }
                
                # Guardar en histórico (ETAPA 6)
                save_task_result(task_id, benchmark, params, execution_time, True, task_result)
                
                return jsonify(task_result)
                
            except Exception as e:
                log_message(f"Error parseando resultados: {e}", "ERROR")
                
                # Preparar resultado con error de parsing
                task_result = {
                    "status": "completed_with_parse_error",
                    "execution_time": execution_time,
                    "worker_id": WORKER_ID,
                    "timestamp": datetime.now().isoformat(),
                    "raw_output": result.stdout,
                    "parse_error": str(e)
                }
                
                # Guardar en histórico (ETAPA 6)
                save_task_result(task_id, benchmark, params, execution_time, False, task_result, str(e))
                
                return jsonify(task_result)
        else:
            log_message(f"Error ejecutando tarea {task_id}: {result.stderr}", "ERROR")
            
            # Preparar resultado con error
            task_result = {
                "status": "error",
                "error": result.stderr,
                "stdout": result.stdout,
                "return_code": result.returncode,
                "worker_id": WORKER_ID,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar en histórico (ETAPA 6)
            save_task_result(task_id, benchmark, params, execution_time, False, task_result, result.stderr)
            
            return jsonify(task_result), 500
            
    except subprocess.TimeoutExpired:
        # Limpiar tarea actual en caso de timeout
        with current_task_lock:
            current_task = None
        
        # Guardar en histórico (ETAPA 6)
        save_task_result(task_id, benchmark, params, 0.0, False, None, "Task execution timeout")
        
        return jsonify({
            "status": "timeout",
            "error": "Task execution timeout",
            "worker_id": WORKER_ID,
            "timestamp": datetime.now().isoformat()
        }), 408
        
    except Exception as e:
        # Limpiar tarea actual en caso de error
        with current_task_lock:
            current_task = None
        
        log_message(f"Error general: {str(e)}", "ERROR")
        return jsonify({
            "status": "error",
            "error": str(e),
            "worker_id": WORKER_ID,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint para obtener estado detallado del worker"""
    try:
        log_message(f"Status request desde {request.remote_addr}")
        
        # Verificar Docker
        docker_available = False
        image_available = False
        
        try:
            docker_result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=5)
            docker_available = docker_result.returncode == 0
            
            if docker_available:
                image_result = subprocess.run(['docker', 'images', '-q', DOCKER_IMAGE], capture_output=True, text=True, timeout=5)
                image_available = bool(image_result.stdout.strip())
                
        except Exception as e:
            if DEBUG_MODE:
                log_message(f"Error verificando Docker: {e}", "DEBUG")
        
        return jsonify({
            "status": "ready",
            "worker_id": WORKER_ID,
            "docker_available": docker_available,
            "image_available": image_available,
            "docker_image": DOCKER_IMAGE,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "benchmark_python": BENCHMARK_PYTHON,
                "benchmark_cython": BENCHMARK_CYTHON,
                "debug_mode": DEBUG_MODE,
                "verbose_mode": VERBOSE_MODE,
                "using_env_config": USE_ENV_CONFIG
            }
        })
        
    except Exception as e:
        log_message(f"Error en status: {str(e)}", "ERROR")
        return jsonify({
            "status": "error",
            "error": str(e),
            "worker_id": WORKER_ID,
            "timestamp": datetime.now().isoformat()
        }), 500

def get_local_ip():
    """Obtener IP local del worker"""
    try:
        # Crear socket para obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_docker_availability():
    """Verificar si Docker está disponible"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

@app.route('/history', methods=['GET'])
def get_task_history():
    """Endpoint para obtener histórico de tareas (ETAPA 6)"""
    try:
        log_message(f"History request desde {request.remote_addr}")
        
        with task_history_lock:
            # Parámetros de consulta
            limit = request.args.get('limit', 50, type=int)
            status_filter = request.args.get('status', None)  # success, failed, all
            
            # Filtrar histórico
            filtered_history = task_history.copy()
            
            if status_filter == 'success':
                filtered_history = [t for t in filtered_history if t["success"]]
            elif status_filter == 'failed':
                filtered_history = [t for t in filtered_history if not t["success"]]
            
            # Limitar resultados
            if limit > 0:
                filtered_history = filtered_history[-limit:]
            
            return jsonify({
                "worker_id": WORKER_ID,
                "task_history": filtered_history,
                "statistics": get_task_statistics(),
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        log_message(f"Error obteniendo histórico: {str(e)}", "ERROR")
        return jsonify({
            "error": str(e),
            "worker_id": WORKER_ID,
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Obtener IP local
    local_ip = get_local_ip()
    
    # Determinar Worker ID basado en IP si no está configurado
    if WORKER_ID == 'worker-unknown':
        if local_ip == '192.168.1.93':
            WORKER_ID = 'worker-01'
        elif local_ip == '192.168.1.155':
            WORKER_ID = 'worker-02'
        else:
            WORKER_ID = f'worker-{local_ip.replace(".", "-")}'
    
    log_message(f"Iniciando Worker Service")
    log_message(f"Worker ID: {WORKER_ID}")
    log_message(f"IP Local: {local_ip}")
    log_message(f"Docker Image: {DOCKER_IMAGE}")
    log_message(f"Usando configuración .env: {USE_ENV_CONFIG}")
    
    if DEBUG_MODE:
        log_message("Modo DEBUG activado", "DEBUG")
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=DEBUG_MODE)
    except Exception as e:
        log_message(f"Error iniciando servidor: {e}", "ERROR")
        exit(1)
