#!/usr/bin/env python3
"""
Configuración del sistema de orquestación usando archivo .env
"""

import os
import json
from typing import Dict, List, Any

class Config:
    """Clase para manejar la configuración del sistema"""
    
    def __init__(self, env_file=".env"):
        self.env_file = env_file
        self.config = {}
        self.load_env_file()
    
    def load_env_file(self):
        """Cargar variables desde el archivo .env"""
        if not os.path.exists(self.env_file):
            print(f"⚠️  Archivo {self.env_file} no encontrado, usando configuración por defecto")
            return
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorar comentarios y líneas vacías
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remover comillas si existen
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Convertir valores booleanos
                        if value.lower() in ['true', 'false']:
                            value = value.lower() == 'true'
                        # Convertir números
                        elif value.isdigit():
                            value = int(value)
                        
                        self.config[key] = value
                        
        except Exception as e:
            print(f"❌ Error cargando {self.env_file}: {e}")
    
    def get(self, key: str, default=None):
        """Obtener valor de configuración"""
        return self.config.get(key, default)
    
    def get_workers_config(self) -> Dict[str, Any]:
        """Generar configuración de workers desde .env"""
        workers = []
        
        # Worker 1
        if self.get('WORKER_01_IP'):
            workers.append({
                "id": self.get('WORKER_01_ID', 'worker-01'),
                "ip": self.get('WORKER_01_IP'),
                "port": self.get('WORKER_01_PORT', 8080),
                "status": "unknown",
                "last_ping": None
            })
        
        # Worker 2
        if self.get('WORKER_02_IP'):
            workers.append({
                "id": self.get('WORKER_02_ID', 'worker-02'),
                "ip": self.get('WORKER_02_IP'),
                "port": self.get('WORKER_02_PORT', 8080),
                "status": "unknown",
                "last_ping": None
            })
        
        return {
            "workers": workers,
            "orchestrator": {
                "timeout": self.get('ORCHESTRATOR_TIMEOUT', 5),
                "retry_attempts": self.get('ORCHESTRATOR_RETRY_ATTEMPTS', 3),
                "max_concurrent_tasks": self.get('ORCHESTRATOR_MAX_CONCURRENT_TASKS', 10)
            }
        }
    
    def get_docker_config(self) -> Dict[str, str]:
        """Configuración de Docker"""
        return {
            "image_name": self.get('DOCKER_IMAGE_NAME', 'particle-simulation'),
            "image_tag": self.get('DOCKER_IMAGE_TAG', 'latest'),
            "full_image": f"{self.get('DOCKER_IMAGE_NAME', 'particle-simulation')}:{self.get('DOCKER_IMAGE_TAG', 'latest')}"
        }
    
    def get_default_simulation_params(self) -> Dict[str, int]:
        """Parámetros por defecto para simulación"""
        return {
            "num_particles": self.get('DEFAULT_NUM_PARTICLES', 100),
            "num_steps": self.get('DEFAULT_NUM_STEPS', 500),
            "seed": self.get('DEFAULT_SEED', 42)
        }
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Configuración de timeouts"""
        return {
            "http_timeout": self.get('HTTP_TIMEOUT', 10),
            "task_timeout": self.get('TASK_TIMEOUT', 60)
        }
    
    def get_benchmark_config(self) -> Dict[str, str]:
        """Configuración de benchmarks"""
        return {
            "python": self.get('BENCHMARK_PYTHON', 'benchmark.py'),
            "cython": self.get('BENCHMARK_CYTHON', 'benchmark_cython.py')
        }
    
    def get_elastic_config(self) -> Dict[str, Any]:
        """Obtener configuración para el sistema elástico (ETAPA 5)"""
        return {
            "ping_interval": self.config.get("ELASTIC_PING_INTERVAL", 5),
            "health_check_interval": self.config.get("ELASTIC_HEALTH_CHECK_INTERVAL", 10),
            "max_ping_failures": self.config.get("ELASTIC_MAX_PING_FAILURES", 5),
            "health_timeout": self.config.get("ELASTIC_HEALTH_TIMEOUT", 30),
            "log_file": self.config.get("ELASTIC_LOG_FILE", "logs/elastic_orchestrator.log"),
            "state_file": self.config.get("WORKER_STATE_FILE", "logs/worker_state.json")
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtener configuración de logging"""
        return {
            "log_level": self.config.get("LOG_LEVEL", "INFO"),
            "log_file": self.config.get("LOG_FILE", "logs/orchestrator.log"),
            "elastic_log_file": self.config.get("ELASTIC_LOG_FILE", "logs/elastic_orchestrator.log"),
            "worker_log_dir": self.config.get("WORKER_LOG_DIR", "logs")
        }
    
    def is_debug_mode(self) -> bool:
        """Verificar si está en modo debug"""
        return self.get('DEBUG_MODE', False)
    
    def is_verbose(self) -> bool:
        """Verificar si está en modo verbose"""
        return self.get('VERBOSE_OUTPUT', True)
    
    def save_to_json(self, filename: str = None):
        """Guardar configuración actual en formato JSON"""
        if filename is None:
            filename = self.get('CONFIG_FILE', 'config_workers.json')
        
        config_data = self.get_workers_config()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuración guardada en {filename}")
            return True
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def print_config(self):
        """Imprimir configuración actual"""
        print("🔧 CONFIGURACIÓN ACTUAL")
        print("=" * 50)
        
        workers = self.get_workers_config()['workers']
        print(f"👥 Workers configurados: {len(workers)}")
        for worker in workers:
            print(f"   - {worker['id']}: {worker['ip']}:{worker['port']}")
        
        docker = self.get_docker_config()
        print(f"🐳 Docker: {docker['full_image']}")
        
        timeouts = self.get_timeout_config()
        print(f"⏱️  Timeouts: HTTP={timeouts['http_timeout']}s, Task={timeouts['task_timeout']}s")
        
        defaults = self.get_default_simulation_params()
        print(f"🎯 Simulación por defecto: {defaults['num_particles']} partículas, {defaults['num_steps']} pasos")
        
        print(f"🐛 Debug: {'Activado' if self.is_debug_mode() else 'Desactivado'}")
        print(f"📝 Verbose: {'Activado' if self.is_verbose() else 'Desactivado'}")
        
        print("=" * 50)

# Instancia global de configuración
config = Config()

# Función de conveniencia para obtener la configuración
def get_config() -> Config:
    """Obtener la instancia de configuración"""
    return config

# Función para recargar configuración
def reload_config():
    """Recargar configuración desde archivo .env"""
    global config
    config = Config()
    return config

if __name__ == "__main__":
    # Prueba de la configuración
    print("🧪 PRUEBA DE CONFIGURACIÓN")
    config.print_config()
    
    # Generar archivo JSON desde .env
    print("\n📄 Generando config_workers.json desde .env...")
    config.save_to_json()
