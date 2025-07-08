#!/usr/bin/env python3
"""
Script para generar config_workers.json desde archivo .env
"""

import sys
import os
from config_manager import get_config

def main():
    print("🔧 GENERADOR DE CONFIG_WORKERS.JSON")
    print("=" * 50)
    
    # Cargar configuración desde .env
    config = get_config()
    
    # Mostrar configuración actual
    config.print_config()
    
    # Generar archivo JSON
    print("\n📄 Generando config_workers.json...")
    
    if config.save_to_json():
        print("✅ Archivo config_workers.json generado exitosamente")
        print("💡 Ahora puedes usar el orquestador con:")
        print("   python3 orchestrator.py")
    else:
        print("❌ Error generando archivo config_workers.json")
        sys.exit(1)
    
    # Verificar que el archivo se generó correctamente
    if os.path.exists('config_workers.json'):
        print("\n📋 Contenido del archivo generado:")
        with open('config_workers.json', 'r') as f:
            content = f.read()
            print(content)
    
    print("\n🎉 Proceso completado")

if __name__ == "__main__":
    main()
