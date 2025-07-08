#!/usr/bin/env python3
"""
Script de verificación para ETAPA 6
Verifica que todos los componentes estén listos para el despliegue
"""

import os
import sys
import json
import requests
from pathlib import Path
import subprocess

def check_file_exists(filename):
    """Verificar que un archivo existe"""
    path = Path(filename)
    if path.exists():
        print(f"✅ {filename} - Encontrado")
        return True
    else:
        print(f"❌ {filename} - NO ENCONTRADO")
        return False

def check_directory_exists(dirname):
    """Verificar que un directorio existe"""
    path = Path(dirname)
    if path.exists():
        print(f"✅ {dirname}/ - Directorio existe")
        return True
    else:
        print(f"⚠️  {dirname}/ - Directorio no existe, creándolo...")
        path.mkdir(parents=True, exist_ok=True)
        return True

def check_config_file(filename):
    """Verificar que un archivo de configuración es válido"""
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                json.load(f)
            else:
                f.read()
        print(f"✅ {filename} - Configuración válida")
        return True
    except Exception as e:
        print(f"❌ {filename} - Error en configuración: {e}")
        return False

def check_python_dependencies():
    """Verificar dependencias de Python"""
    try:
        import requests
        import flask
        import threading
        print("✅ Dependencias de Python - OK")
        return True
    except ImportError as e:
        print(f"❌ Dependencias de Python - Falta: {e}")
        return False

def check_port_availability(port):
    """Verificar que un puerto esté disponible"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            print(f"⚠️  Puerto {port} - En uso")
            return False
        else:
            print(f"✅ Puerto {port} - Disponible")
            return True
    except Exception as e:
        print(f"❌ Puerto {port} - Error verificando: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DEL SISTEMA ETAPA 6")
    print("=" * 50)
    
    all_good = True
    
    # 1. Verificar archivos principales
    print("\n📁 Verificando archivos principales...")
    required_files = [
        "elastic_orchestrator_v6.py",
        "worker_service.py",
        "config_manager.py",
        "task_generator.py",
        ".env",
        "config_workers.json",
        "requirements.txt",
        "requirements_worker.txt",
        "start_elastic_orchestrator_v6.sh",
        "start_worker.sh",
        "README_ETAPA6.md"
    ]
    
    for file in required_files:
        if not check_file_exists(file):
            all_good = False
    
    # 2. Verificar directorios necesarios
    print("\n📂 Verificando directorios...")
    required_dirs = ["logs", "results"]
    for dir_name in required_dirs:
        check_directory_exists(dir_name)
    
    # 3. Verificar configuración
    print("\n⚙️  Verificando configuración...")
    config_files = [".env", "config_workers.json"]
    for file in config_files:
        if not check_config_file(file):
            all_good = False
    
    # 4. Verificar dependencias de Python
    print("\n🐍 Verificando dependencias de Python...")
    if not check_python_dependencies():
        all_good = False
    
    # 5. Verificar puertos disponibles
    print("\n🔌 Verificando puertos...")
    ports = [5000, 5001, 5002, 5003]  # Orchestrator y workers
    for port in ports:
        check_port_availability(port)
    
    # 6. Verificar archivos de benchmark
    print("\n🏃 Verificando benchmarks...")
    benchmark_files = ["benchmark.py", "benchmark_cython.py"]
    for file in benchmark_files:
        if not check_file_exists(file):
            all_good = False
    
    # 7. Verificar que los scripts son ejecutables
    print("\n🔧 Verificando permisos de scripts...")
    script_files = [
        "start_elastic_orchestrator_v6.sh",
        "start_worker.sh"
    ]
    for script in script_files:
        if os.path.exists(script):
            try:
                os.chmod(script, 0o755)
                print(f"✅ {script} - Permisos configurados")
            except Exception as e:
                print(f"❌ {script} - Error configurando permisos: {e}")
                all_good = False
    
    # 8. Resumen final
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SISTEMA LISTO PARA ETAPA 6")
        print("\n📋 Próximos pasos:")
        print("1. En máquina maestro: ./start_elastic_orchestrator_v6.sh")
        print("2. En máquinas worker: ./start_worker.sh")
        print("3. Generar tareas: python task_generator.py")
        print("4. Monitorear: curl http://localhost:5000/stats")
        return 0
    else:
        print("❌ SISTEMA NO ESTÁ LISTO")
        print("Por favor, resolver los errores antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())
