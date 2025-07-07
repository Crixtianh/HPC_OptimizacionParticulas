#!/usr/bin/env python3
"""
Cliente para interactuar con el orquestador
"""

import requests
import json
import time
import argparse
from datetime import datetime

class OrchestratorClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_status(self):
        """Obtener estado del sistema"""
        try:
            response = requests.get(f"{self.base_url}/status")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def ping_workers(self):
        """Hacer ping a todos los workers"""
        try:
            response = requests.get(f"{self.base_url}/ping_all")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def execute_tasks(self):
        """Ejecutar todas las tareas"""
        try:
            response = requests.post(f"{self.base_url}/execute_tasks")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_workers(self):
        """Obtener información de workers"""
        try:
            response = requests.get(f"{self.base_url}/workers")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def print_json(data):
    """Imprimir JSON de forma legible"""
    print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Cliente del Orquestador')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='URL base del orquestador')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando status
    subparsers.add_parser('status', help='Obtener estado del sistema')
    
    # Comando ping
    subparsers.add_parser('ping', help='Hacer ping a workers')
    
    # Comando execute
    subparsers.add_parser('execute', help='Ejecutar tareas')
    
    # Comando workers
    subparsers.add_parser('workers', help='Obtener información de workers')
    
    # Comando monitor
    monitor_parser = subparsers.add_parser('monitor', help='Monitorear sistema')
    monitor_parser.add_argument('--interval', type=int, default=10,
                               help='Intervalo de monitoreo en segundos')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = OrchestratorClient(args.url)
    
    if args.command == 'status':
        print("=== Estado del Sistema ===")
        status = client.get_status()
        print_json(status)
        
    elif args.command == 'ping':
        print("=== Ping a Workers ===")
        ping_result = client.ping_workers()
        print_json(ping_result)
        
    elif args.command == 'execute':
        print("=== Ejecutando Tareas ===")
        result = client.execute_tasks()
        print_json(result)
        
    elif args.command == 'workers':
        print("=== Información de Workers ===")
        workers = client.get_workers()
        print_json(workers)
        
    elif args.command == 'monitor':
        print(f"=== Monitoreando Sistema (cada {args.interval}s) ===")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}]")
                
                status = client.get_status()
                if 'error' not in status:
                    online = status.get('online_workers', 0)
                    total = status.get('total_workers', 0)
                    print(f"Workers: {online}/{total} online")
                    
                    # Hacer ping
                    ping_result = client.ping_workers()
                    if 'error' not in ping_result:
                        worker_status = ping_result.get('status', {})
                        for worker_id, status_val in worker_status.items():
                            print(f"  {worker_id}: {status_val}")
                else:
                    print(f"Error: {status['error']}")
                
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")

if __name__ == '__main__':
    main()
