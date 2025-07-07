#!/usr/bin/env python3
"""
Servicio Worker para ejecutar simulaciones
"""

import json
import subprocess
import tempfile
import os
import sys
import argparse
from flask import Flask, jsonify, request
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimulationWorker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.current_task = None
        
    def ping(self):
        """Responder a ping de salud"""
        return {
            'status': 'online',
            'worker_id': self.worker_id,
            'timestamp': datetime.now().isoformat(),
            'current_task': self.current_task
        }
    
    def execute_simulation(self, task: dict):
        """Ejecutar simulación basada en parámetros de tarea"""
        try:
            self.current_task = task.get('id', 'unknown')
            logger.info(f"Ejecutando tarea: {self.current_task}")
            
            task_type = task.get('type', 'benchmark')
            parameters = task.get('parameters', {})
            
            # Construir comando
            if task_type == 'benchmark':
                script = 'benchmark.py'
            elif task_type == 'benchmark_cython':
                script = 'benchmark_cython.py'
            else:
                raise ValueError(f"Tipo de tarea desconocido: {task_type}")
            
            # Parámetros de la simulación
            num_particulas = parameters.get('num_particulas', 100)
            num_pasos = parameters.get('num_pasos', 1000)
            semilla = parameters.get('semilla', 42)
            
            # Ejecutar comando
            cmd = ['python', script, str(num_particulas), str(num_pasos), str(semilla)]
            logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            end_time = datetime.now()
            
            # Procesar resultado
            if result.returncode == 0:
                # Parsear salida para extraer métricas
                output_lines = result.stdout.strip().split('\n')
                metrics = self._parse_simulation_output(output_lines)
                
                response = {
                    'success': True,
                    'worker_id': self.worker_id,
                    'task_id': task.get('id'),
                    'task_type': task_type,
                    'parameters': parameters,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': (end_time - start_time).total_seconds(),
                    'metrics': metrics,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
                logger.info(f"Tarea {self.current_task} completada exitosamente")
                return response
            else:
                logger.error(f"Error ejecutando tarea: {result.stderr}")
                return {
                    'success': False,
                    'worker_id': self.worker_id,
                    'task_id': task.get('id'),
                    'error': result.stderr,
                    'stdout': result.stdout,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ejecutando tarea {self.current_task}")
            return {
                'success': False,
                'worker_id': self.worker_id,
                'task_id': task.get('id'),
                'error': 'Timeout ejecutando simulación'
            }
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {
                'success': False,
                'worker_id': self.worker_id,
                'task_id': task.get('id'),
                'error': str(e)
            }
        finally:
            self.current_task = None
    
    def _parse_simulation_output(self, output_lines):
        """Parsear salida de simulación para extraer métricas"""
        metrics = {}
        
        for line in output_lines:
            if 'completada en' in line and 'segundos' in line:
                # Extraer tiempo de ejecución
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'segundos' in part and i > 0:
                        try:
                            metrics['execution_time'] = float(parts[i-1])
                        except ValueError:
                            pass
            elif 'Total colisiones Partícula-Partícula:' in line:
                try:
                    metrics['particle_collisions'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif 'Total colisiones con Pared:' in line:
                try:
                    metrics['wall_collisions'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif 'Total pasos:' in line:
                try:
                    parts = line.split(',')
                    steps_part = parts[0].split(':')[1].strip()
                    metrics['total_steps'] = int(steps_part)
                    
                    if len(parts) > 1 and 'Partículas:' in parts[1]:
                        particles_part = parts[1].split(':')[1].strip()
                        metrics['total_particles'] = int(particles_part)
                except (ValueError, IndexError):
                    pass
        
        return metrics

# Crear instancia global del worker
worker = None

# Flask app
app = Flask(__name__)

@app.route('/ping')
def ping():
    """Endpoint de ping para health check"""
    return jsonify(worker.ping())

@app.route('/execute', methods=['POST'])
def execute():
    """Endpoint para ejecutar simulación"""
    try:
        task = request.get_json()
        if not task:
            return jsonify({'error': 'No se proporcionó tarea'}), 400
        
        result = worker.execute_simulation(task)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error procesando request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Endpoint de estado del worker"""
    return jsonify({
        'worker_id': worker.worker_id,
        'status': 'running',
        'current_task': worker.current_task,
        'timestamp': datetime.now().isoformat()
    })

def main():
    """Función principal"""
    global worker
    
    parser = argparse.ArgumentParser(description='Worker de simulación')
    parser.add_argument('--port', type=int, default=8000, help='Puerto del servidor')
    parser.add_argument('--worker-id', required=True, help='ID del worker')
    
    args = parser.parse_args()
    
    # Crear worker
    worker = SimulationWorker(args.worker_id)
    
    logger.info(f"Iniciando worker {args.worker_id} en puerto {args.port}")
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()
