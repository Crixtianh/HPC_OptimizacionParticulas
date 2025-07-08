#!/usr/bin/env python3
"""
Monitor en tiempo real para el sistema elástico ETAPA 5
Muestra el estado de los workers y estadísticas en tiempo real
"""

import os
import json
import time
import requests
from datetime import datetime
from config_manager import get_config

class ElasticMonitor:
    """Monitor en tiempo real para el sistema elástico"""
    
    def __init__(self):
        self.config = get_config()
        self.workers_config = self.config.get_workers_config()
        self.workers = self.workers_config['workers']
        self.timeout = self.config.get_timeout_config()['http_timeout']
        self.state_file = "logs/worker_state.json"
        
    def clear_screen(self):
        """Limpiar pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_worker_state(self):
        """Obtener estado actual de workers desde archivo"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            return {"error": str(e)}
    
    def ping_worker(self, worker):
        """Ping directo a un worker"""
        try:
            url = f"http://{worker['ip']}:{worker['port']}/ping"
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "response_time": response_time,
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e)
            }
    
    def format_uptime(self, uptime_str):
        """Formatear tiempo de actividad"""
        try:
            uptime_start = datetime.fromisoformat(uptime_str.replace('Z', '+00:00'))
            uptime = datetime.now() - uptime_start
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m {seconds}s"
            elif hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return uptime_str
    
    def display_header(self):
        """Mostrar header"""
        print("🎭 MONITOR SISTEMA ELÁSTICO - ETAPA 5")
        print("=" * 60)
        print(f"🕐 Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def display_workers_status(self, state):
        """Mostrar estado de workers"""
        print("\n🖥️  ESTADO DE WORKERS:")
        print("-" * 60)
        
        if not state or "workers" not in state:
            print("❌ No hay datos de estado disponibles")
            return
        
        workers = state["workers"]
        for worker_id, worker_data in workers.items():
            # Icono de estado
            status = worker_data.get("status", "unknown")
            if status == "active":
                icon = "✅"
            elif status == "inactive":
                icon = "❌"
            elif status == "unstable":
                icon = "⚠️"
            else:
                icon = "❓"
            
            # Información básica
            print(f"{icon} {worker_id} ({worker_data['ip']}:{worker_data['port']})")
            print(f"   Estado: {status}")
            
            # Tiempo de respuesta
            avg_response = worker_data.get("average_response_time", 0)
            if avg_response > 0:
                print(f"   Tiempo respuesta: {avg_response:.3f}s")
            
            # Último ping
            last_ping = worker_data.get("last_ping")
            if last_ping:
                try:
                    last_ping_dt = datetime.fromisoformat(last_ping.replace('Z', '+00:00'))
                    time_since = datetime.now() - last_ping_dt
                    print(f"   Último ping: hace {time_since.seconds}s")
                except:
                    print(f"   Último ping: {last_ping}")
            
            # Fallos consecutivos
            failures = worker_data.get("consecutive_failures", 0)
            if failures > 0:
                print(f"   Fallos consecutivos: {failures}")
            
            # Tareas completadas
            tasks = worker_data.get("total_tasks_completed", 0)
            if tasks > 0:
                print(f"   Tareas completadas: {tasks}")
            
            # Salud
            is_healthy = worker_data.get("is_healthy", False)
            health_icon = "💚" if is_healthy else "💔"
            print(f"   Salud: {health_icon}")
            
            print()
    
    def display_statistics(self, state):
        """Mostrar estadísticas del sistema"""
        print("📊 ESTADÍSTICAS DEL SISTEMA:")
        print("-" * 60)
        
        if not state or "stats" not in state:
            print("❌ No hay estadísticas disponibles")
            return
        
        stats = state["stats"]
        
        # Tiempo de actividad
        uptime_start = stats.get("uptime_start")
        if uptime_start:
            uptime_formatted = self.format_uptime(uptime_start)
            print(f"⏱️  Tiempo activo: {uptime_formatted}")
        
        # Estadísticas de ping
        total_pings = stats.get("total_pings", 0)
        successful_pings = stats.get("successful_pings", 0)
        failed_pings = stats.get("failed_pings", 0)
        
        if total_pings > 0:
            success_rate = (successful_pings / total_pings) * 100
            print(f"📈 Pings totales: {total_pings}")
            print(f"✅ Pings exitosos: {successful_pings}")
            print(f"❌ Pings fallidos: {failed_pings}")
            print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        # Descubrimiento de workers
        discovered = stats.get("workers_discovered", 0)
        lost = stats.get("workers_lost", 0)
        
        if discovered > 0 or lost > 0:
            print(f"🔗 Workers descubiertos: {discovered}")
            print(f"💔 Workers perdidos: {lost}")
    
    def display_live_ping(self):
        """Mostrar ping en vivo"""
        print("\n🔄 PING EN VIVO:")
        print("-" * 60)
        
        for worker in self.workers:
            result = self.ping_worker(worker)
            
            if result["status"] == "online":
                icon = "✅"
                info = f"{result['response_time']:.3f}s"
            elif result["status"] == "error":
                icon = "⚠️"
                info = result["error"]
            else:
                icon = "❌"
                info = result["error"]
            
            print(f"{icon} {worker['id']} ({worker['ip']}): {info}")
    
    def display_footer(self):
        """Mostrar footer"""
        print("\n" + "=" * 60)
        print("🔄 Actualizando cada 5 segundos... (Ctrl+C para salir)")
        print("=" * 60)
    
    def run(self):
        """Ejecutar monitor en tiempo real"""
        print("🚀 Iniciando monitor en tiempo real...")
        print("   Presiona Ctrl+C para salir")
        
        try:
            while True:
                self.clear_screen()
                
                # Header
                self.display_header()
                
                # Obtener estado desde archivo
                state = self.get_worker_state()
                
                # Mostrar estado de workers
                self.display_workers_status(state)
                
                # Mostrar estadísticas
                self.display_statistics(state)
                
                # Mostrar ping en vivo
                self.display_live_ping()
                
                # Footer
                self.display_footer()
                
                # Esperar 5 segundos
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor detenido por el usuario")
        except Exception as e:
            print(f"\n❌ Error en monitor: {e}")

def main():
    """Función principal"""
    monitor = ElasticMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
