# SISTEMA DE ORQUESTACIÓN ELÁSTICA - VERSIÓN FINAL
# ETAPA 6: COLA DE TAREAS DISTRIBUIDA CON INGRESO MANUAL

## 🎯 Descripción General

Este sistema implementa una arquitectura de orquestación elástica completa para simulación de partículas distribuida. La versión final (ETAPA 6) se caracteriza por:

- **📋 Cola de tareas manual**: Gestión de tareas cargadas exclusivamente desde archivos JSON
- **🔄 Distribución automática**: Asignación inteligente de tareas a workers disponibles
- **💾 Almacenamiento persistente**: Resultados y métricas almacenados en disco
- **⚖️ Balanceamiento de carga**: Distribución eficiente basada en capacidad de workers
- **🔧 Recuperación de fallos**: Reintentos automáticos y redistribución de tareas
- **📊 Métricas en tiempo real**: Monitoreo detallado de rendimiento y estado
- **🎛️ Modo manual exclusivo**: Sin generación automática de tareas

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SISTEMA DE ORQUESTACIÓN ELÁSTICA                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   Orchestrator  │    │     Worker 1    │    │     Worker 2    │          │
│  │   (Maestro)     │    │   (5001)        │    │   (5002)        │          │
│  │   (Puerto 5000) │    │                 │    │                 │          │
│  │                 │    │                 │    │                 │          │
│  │ • Task Queue    │◄──►│ • Task Executor │    │ • Task Executor │          │
│  │ • Load Balancer │    │ • Results Store │    │ • Results Store │          │
│  │ • Fault Recovery│    │ • Performance   │    │ • Performance   │          │
│  │ • File Monitor  │    │   Metrics       │    │   Metrics       │          │
│  │ • Statistics    │    │ • Health Check  │    │ • Health Check  │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │  task_queues/   │ ← Archivos JSON ingresados manualmente                │
│  │  ├─ ejemplo.json │                                                       │
│  │  ├─ tareas.json  │                                                       │
│  │  └─ processed/   │ ← Archivos procesados automáticamente                 │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📦 Componentes Principales

### 1. 🎛️ Orchestrator (Maestro)
- **Archivo**: `elastic_orchestrator_v6.py`
- **Puerto**: 5000
- **Funciones**:
  - Monitoreo del directorio `task_queues/`
  - Distribución automática de tareas
  - Balanceamiento de carga entre workers
  - Recuperación de fallos y reintentos
  - Estadísticas en tiempo real
  - API REST para monitoreo

### 2. 👷 Workers (Trabajadores)
- **Archivo**: `worker_service.py`
- **Puertos**: 5001, 5002, 5003, etc.
- **Funciones**:
  - Ejecución de algoritmos (Python/Cython)
  - Reporte de resultados y métricas
  - Health checks periódicos
  - Historial de tareas

### 3. 📝 Manual Task Generator
- **Archivo**: `manual_task_generator.py`
- **Función**: Herramienta interactiva para crear archivos JSON con tareas

### 4. 🗂️ Sistema de Archivos
- **Directorio**: `task_queues/`
- **Archivos de ejemplo**: `tareas_manuales_ejemplo.json`
- **Procesados**: `task_queues/processed/`

## ⚙️ Configuración del Sistema

### Variables de Entorno (.env)
```bash
# CONFIGURACIÓN PRINCIPAL
TASK_DISTRIBUTION_INTERVAL=2.0      # Intervalo de distribución (segundos)
MAX_TASK_RETRIES=3                  # Máximo reintentos por tarea
RESULTS_STORAGE_PATH=results/       # Directorio de resultados
WORKER_TIMEOUT=300                  # Timeout de workers (segundos)
LOAD_BALANCING_ALGORITHM=round_robin # Algoritmo de balanceamiento
PERFORMANCE_MONITORING=true         # Monitoreo de rendimiento
MANUAL_MODE=true                    # Modo manual (sin auto-generación)

# CONFIGURACIÓN DE WORKERS
WORKER_01_IP=192.168.1.100         # IP del worker 1
WORKER_01_PORT=5001                 # Puerto del worker 1
WORKER_02_IP=192.168.1.101         # IP del worker 2
WORKER_02_PORT=5002                 # Puerto del worker 2

# CONFIGURACIÓN DE LOGGING
LOG_LEVEL=INFO                      # Nivel de logging
ELASTIC_LOG_FILE=logs/elastic_orchestrator.log
```

### Configuración de Workers (config_workers.json)
```json
{
  "workers": [
    {
      "id": "worker-01",
      "ip": "192.168.1.100",
      "port": 5001,
      "status": "unknown",
      "capacity": 2,
      "algorithms": ["python", "cython"]
    },
    {
      "id": "worker-02",
      "ip": "192.168.1.101",
      "port": 5002,
      "status": "unknown",
      "capacity": 4,
      "algorithms": ["python", "cython"]
    }
  ],
  "orchestrator": {
    "timeout": 30,
    "retry_attempts": 3,
    "max_concurrent_tasks": 10
  }
}
```

## 🚀 Instalación y Despliegue

### Preparación del Entorno
```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd TAREA

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear directorios necesarios
mkdir -p logs results task_queues task_queues/processed

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con las IPs y configuraciones apropiadas
```

### Iniciar el Sistema

#### Máquina del Orchestrator
```bash
# Iniciar el orchestrator
python elastic_orchestrator_v6.py

# Verificar funcionamiento
curl http://localhost:5000/health
```

#### Máquinas Worker
```bash
# Worker 1
python worker_service.py --worker-id worker-01 --port 5001

# Worker 2
python worker_service.py --worker-id worker-02 --port 5002
```

## 📋 Uso del Sistema - Modo Manual

### 1. Crear Tareas

#### Opción 1: Usar Archivo de Ejemplo
```bash
# Copiar archivo de ejemplo
cp tareas_manuales_ejemplo.json task_queues/

# El orchestrator procesará automáticamente
```

#### Opción 2: Generar Tareas Personalizadas
```bash
# Usar el generador interactivo
python manual_task_generator.py

# Seguir las instrucciones para crear tareas personalizadas
```

#### Opción 3: Crear Manualmente
```json
{
  "metadata": {
    "creation_date": "2024-07-08",
    "description": "Lote de tareas de simulación",
    "total_tasks": 3,
    "created_by": "Usuario Manual"
  },
  "tasks": [
    {
      "task_id": "sim_001",
      "algorithm": "python",
      "parameters": {
        "num_particles": 100,
        "num_steps": 500,
        "seed": 123
      },
      "priority": "high",
      "description": "Simulación rápida Python"
    },
    {
      "task_id": "sim_002",
      "algorithm": "cython",
      "parameters": {
        "num_particles": 200,
        "num_steps": 800,
        "seed": 456
      },
      "priority": "medium",
      "description": "Simulación optimizada Cython"
    }
  ]
}
```

### 2. Monitorear el Sistema

#### Estadísticas del Orchestrator
```bash
# Estado general
curl http://localhost:5000/stats

# Lista de tareas
curl http://localhost:5000/tasks

# Estado de workers
curl http://localhost:5000/workers

# Salud del sistema
curl http://localhost:5000/health
```

#### Estado de Workers
```bash
# Estado del worker
curl http://worker-ip:5001/status

# Historial de tareas
curl http://worker-ip:5001/history

# Métricas de rendimiento
curl http://worker-ip:5001/metrics
```

### 3. Workflow Completo

#### Paso 1: Preparar Tareas
```bash
# Crear archivo JSON con tareas
python manual_task_generator.py

# O copiar archivo de ejemplo
cp tareas_manuales_ejemplo.json task_queues/mi_lote_$(date +%Y%m%d_%H%M%S).json
```

#### Paso 2: Verificar Ingreso
```bash
# Verificar archivo procesado
ls task_queues/processed/

# Ver estadísticas
curl http://localhost:5000/stats
```

#### Paso 3: Monitorear Ejecución
```bash
# Ver progreso en tiempo real
watch -n 2 "curl -s http://localhost:5000/stats | jq '.tasks_summary'"

# Ver logs
tail -f logs/elastic_orchestrator.log
```

#### Paso 4: Revisar Resultados
```bash
# Ver archivos de resultados
ls results/

# Analizar resultados específicos
cat results/task_results_$(date +%Y%m%d)_*.json | jq '.'
```

## 📊 Estructura de Resultados

### Directorios y Archivos
```
TAREA/
├── results/                          # Resultados de ejecución
│   ├── task_results_20240708_143000.json
│   ├── task_results_20240708_144000.json
│   └── orchestrator_stats.json
├── task_queues/                      # Cola de tareas manual
│   ├── tareas_manuales_ejemplo.json  # Archivo de ejemplo
│   ├── mi_lote_20240708_143000.json  # Archivos personalizados
│   └── processed/                    # Archivos procesados
│       ├── 20240708_143000_tareas_manuales_ejemplo.json
│       └── 20240708_143500_mi_lote_20240708_143000.json
├── logs/                             # Logs del sistema
│   ├── elastic_orchestrator.log      # Logs del orchestrator
│   └── worker_state.json             # Estado de workers
└── __pycache__/                      # Archivos compilados Python
```

### Formato de Resultados
```json
{
  "timestamp": "2024-07-08T14:30:00",
  "orchestrator_stats": {
    "total_tasks": 10,
    "completed_tasks": 8,
    "failed_tasks": 1,
    "pending_tasks": 1,
    "active_workers": 2,
    "total_execution_time": 450.2
  },
  "task_results": [
    {
      "task_id": "sim_001",
      "algorithm": "python",
      "parameters": {
        "num_particles": 100,
        "num_steps": 500,
        "seed": 123
      },
      "execution_time": 45.8,
      "result": {
        "status": "completed",
        "output": "Simulación completada exitosamente",
        "metrics": {
          "particles_processed": 100,
          "steps_completed": 500,
          "memory_peak": "67.2 MB"
        }
      },
      "worker_id": "worker-01",
      "completed_at": "2024-07-08T14:25:30",
      "priority": "high"
    }
  ]
}
```

## 🔧 Funcionalidades Avanzadas

### 1. Sistema de Prioridades
- **High**: Tareas ejecutadas primero
- **Medium**: Prioridad estándar
- **Low**: Ejecutadas cuando hay capacidad disponible

### 2. Recuperación de Fallos
- Reintentos automáticos hasta 3 veces
- Redistribución a otros workers disponibles
- Logging detallado de errores

### 3. Balanceamiento de Carga
- Algoritmo round-robin por defecto
- Distribución basada en capacidad de workers
- Monitoreo de carga en tiempo real

### 4. Monitoreo Continuo
- Health checks cada 5 segundos
- Detección automática de workers caídos
- Rebalanceo automático de tareas

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Archivos JSON no se procesan
```bash
# Verificar directorio
ls -la task_queues/

# Validar formato JSON
python -m json.tool task_queues/mi_archivo.json

# Revisar logs
tail -f logs/elastic_orchestrator.log
```

#### 2. Workers no responden
```bash
# Verificar conectividad
curl http://worker-ip:5001/health

# Verificar logs
tail -f logs/worker_service.log

# Reiniciar worker
python worker_service.py --worker-id worker-01 --port 5001
```

#### 3. Tareas fallan constantemente
```bash
# Ver tareas fallidas
curl http://localhost:5000/tasks | jq '.[] | select(.status=="failed")'

# Verificar parámetros en JSON
python -c "import json; print(json.load(open('task_queues/mi_archivo.json'))['tasks'][0]['parameters'])"
```

### Comandos de Diagnóstico
```bash
# Estado completo del sistema
curl http://localhost:5000/stats | jq '.'

# Logs en tiempo real
tail -f logs/elastic_orchestrator.log

# Verificar workers activos
curl http://localhost:5000/workers | jq '.[] | select(.status=="active")'

# Verificar espacio en disco
df -h results/ logs/
```

## 🧪 Pruebas y Validación

### Pruebas Básicas
```bash
# 1. Prueba de conectividad
python test_communication.py

# 2. Prueba con archivo de ejemplo
cp tareas_manuales_ejemplo.json task_queues/test_$(date +%s).json

# 3. Monitorear procesamiento
watch -n 2 "curl -s http://localhost:5000/stats | jq '.tasks_summary'"
```

### Pruebas de Carga
```bash
# Generar múltiples archivos de tareas
for i in {1..5}; do
  python manual_task_generator.py
done

# Verificar procesamiento
ls task_queues/processed/
```

### Pruebas de Recuperación
```bash
# Simular falla de worker (detener worker durante ejecución)
# Verificar redistribución automática
curl http://localhost:5000/tasks | jq '.[] | select(.status=="redistributed")'
```

## 🔧 Mantenimiento del Sistema

### Limpieza Regular
```bash
# Limpiar archivos procesados antiguos (> 7 días)
find task_queues/processed/ -name "*.json" -mtime +7 -delete

# Rotar logs
mv logs/elastic_orchestrator.log logs/elastic_orchestrator_$(date +%Y%m%d).log
touch logs/elastic_orchestrator.log

# Limpiar resultados antiguos
find results/ -name "*.json" -mtime +30 -delete
```

### Monitoreo de Salud
```bash
# Script de monitoreo automático
#!/bin/bash
while true; do
  echo "$(date): Verificando salud del sistema..."
  curl -s http://localhost:5000/health || echo "⚠️ Orchestrator no responde"
  curl -s http://worker1:5001/health || echo "⚠️ Worker 1 no responde"
  curl -s http://worker2:5002/health || echo "⚠️ Worker 2 no responde"
  sleep 60
done
```

## 📂 ARCHIVOS OBSOLETOS - LISTOS PARA ELIMINAR

Los siguientes archivos son de versiones anteriores del sistema y ya no son necesarios para la **versión final (ETAPA 6)**:

### 🗑️ Archivos de Etapas Anteriores
```bash
# Orchestrators obsoletos
rm elastic_orchestrator.py          # Versión anterior
rm orchestrator.py                  # Versión original
rm monitor_elastic.py               # Monitor obsoleto

# Scripts de inicio obsoletos
rm start_elastic_orchestrator.sh    # Script anterior
rm start_elastic_orchestrator.bat   # Script anterior
rm start_etapa6_auto.py            # Auto-generación (deshabilitada)
rm start_etapa6_auto.bat           # Auto-generación (deshabilitada)

# Generadores obsoletos
rm auto_task_generator.py          # Generación automática (deshabilitada)
rm task_generator.py               # Generador anterior
rm generate_config.py              # Generador de config obsoleto

# Archivos de demostración obsoletos
rm demo_tasks_manual.json          # Reemplazado por tareas_manuales_ejemplo.json

# READMEs de etapas anteriores
rm README_CONFIG.md                # Configuración obsoleta
rm README_ETAPA2.md               # Etapa 2 completada
rm README_ETAPA4.md               # Etapa 4 completada
rm README_ETAPA5.md               # Etapa 5 completada
rm QUICK_START.md                 # Guía rápida obsoleta

# Scripts de testing obsoletos
rm test_etapa6.py                 # Testing específico obsoleto
rm verify_etapa6.py               # Verificación específica obsoleta

# Scripts de despliegue obsoletos
rm deploy_etapa6.bat              # Despliegue específico obsoleto
rm setup_worker_dependencies.sh   # Setup obsoleto
rm package_project.sh             # Empaquetado obsoleto
```

### 🗑️ Archivos de Docker (si no se usa Docker)
```bash
# Solo eliminar si NO usas Docker
rm Dockerfile                     # Dockerfile principal
rm Dockerfile.worker              # Dockerfile para workers
rm build_docker.sh                # Script de construcción Docker
rm build_docker.bat               # Script de construcción Docker
rm test_docker.sh                 # Testing Docker
rm test_docker.bat                # Testing Docker
```

### 🗑️ Archivos de Compilación (si no se usa Cython)
```bash
# Solo eliminar si NO usas Cython
rm engine_cython.c                # Código C generado
rm engine_cython.pyx              # Código Cython fuente
rm engine_cython.cpython-310-x86_64-linux-gnu.so  # Librería compilada
rm setup.py                       # Script de setup para Cython
rm -rf build/                     # Directorio de compilación
```

### 🗑️ Archivos de Profiling y Benchmarking
```bash
# Archivos de análisis de rendimiento (mantener solo si necesitas benchmarking)
rm perfil_base.prof               # Perfil de rendimiento base
rm benchmark.py                   # Benchmark Python (opcional)
rm benchmark_cython.py            # Benchmark Cython (opcional)
```

### 🗑️ Archivos Comprimidos
```bash
# Archivos de backup/distribución
rm particle-simulation-ETAPA4-20250708-005727.tar.gz  # Backup anterior
```

### 🗑️ Directorios de Cache
```bash
# Limpiar cache de Python
rm -rf __pycache__/               # Cache de Python
find . -name "*.pyc" -delete      # Archivos compilados
find . -name "__pycache__" -type d -exec rm -rf {} +  # Todos los cache
```

## 📋 ARCHIVOS ESENCIALES - NO ELIMINAR

Los siguientes archivos son **ESENCIALES** para el funcionamiento del sistema final:

### ✅ Archivos Core del Sistema
```bash
# Componentes principales
elastic_orchestrator_v6.py        # Orchestrator principal
worker_service.py                 # Servicio de workers
config_manager.py                 # Gestor de configuración
simulacion_partic.py              # Simulación de partículas

# Herramientas manuales
manual_task_generator.py          # Generador manual de tareas
tareas_manuales_ejemplo.json      # Archivo de ejemplo

# Configuración
config_workers.json               # Configuración de workers
requirements.txt                  # Dependencias Python
requirements_worker.txt           # Dependencias para workers
.env                             # Variables de entorno

# Scripts de inicio
start_worker.sh                   # Script para iniciar workers
start_worker.bat                  # Script para iniciar workers (Windows)
start_elastic_orchestrator_v6.sh  # Script para iniciar orchestrator

# Testing esencial
test_communication.py             # Testing de comunicación

# Documentación
README_ETAPA6.md                 # Documentación principal
README_FINAL.md                  # Este archivo
```

### ✅ Directorios Esenciales
```bash
# Directorios de funcionamiento
task_queues/                      # Cola de tareas manual
task_queues/processed/            # Archivos procesados
results/                          # Resultados de ejecución
logs/                            # Logs del sistema
```

## 🚀 Comando de Limpieza Automatizada

Para limpiar todos los archivos obsoletos de una vez:

```bash
#!/bin/bash
# limpieza_archivos_obsoletos.sh

echo "🧹 Limpiando archivos obsoletos del sistema..."

# Archivos obsoletos
rm -f elastic_orchestrator.py
rm -f orchestrator.py
rm -f monitor_elastic.py
rm -f start_elastic_orchestrator.sh
rm -f start_elastic_orchestrator.bat
rm -f start_etapa6_auto.py
rm -f start_etapa6_auto.bat
rm -f auto_task_generator.py
rm -f task_generator.py
rm -f generate_config.py
rm -f demo_tasks_manual.json
rm -f README_CONFIG.md
rm -f README_ETAPA2.md
rm -f README_ETAPA4.md
rm -f README_ETAPA5.md
rm -f QUICK_START.md
rm -f test_etapa6.py
rm -f verify_etapa6.py
rm -f deploy_etapa6.bat
rm -f setup_worker_dependencies.sh
rm -f package_project.sh

# Archivos de compilación Cython (descomenta si no usas Cython)
# rm -f engine_cython.c
# rm -f engine_cython.pyx
# rm -f engine_cython.cpython-310-x86_64-linux-gnu.so
# rm -f setup.py
# rm -rf build/

# Archivos de profiling (descomenta si no necesitas benchmarking)
# rm -f perfil_base.prof
# rm -f benchmark.py
# rm -f benchmark_cython.py

# Archivos comprimidos
rm -f particle-simulation-ETAPA4-20250708-005727.tar.gz

# Limpiar cache Python
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ Limpieza completada!"
echo "📋 Archivos esenciales conservados."
echo "🔍 Revisa el README_FINAL.md para más detalles."
```

## 📈 Roadmap y Mejoras Futuras

### Mejoras Planificadas
1. **Interface Web**: Dashboard para monitoreo visual
2. **Notificaciones**: Alertas por email/Slack cuando fallan tareas
3. **Métricas Avanzadas**: Graficas de rendimiento en tiempo real
4. **Escalabilidad**: Auto-scaling de workers basado en carga
5. **Persistencia**: Base de datos para historial de tareas

### Extensiones Posibles
- **Algoritmos adicionales**: Soporte para más tipos de simulación
- **Scheduling avanzado**: Prioridades dinámicas basadas en recursos
- **Distribución geográfica**: Workers en múltiples regiones
- **Integración CI/CD**: Pipeline automatizado para despliegue

## 📞 Contacto y Soporte

Para reportar problemas, sugerencias o contribuciones:

1. **Revisar logs**: `logs/elastic_orchestrator.log`
2. **Verificar configuración**: `config_workers.json` y `.env`
3. **Consultar este README**: Sección de troubleshooting
4. **Testing básico**: `python test_communication.py`

---

## 🎉 Resumen Final

Este sistema de orquestación elástica representa una solución completa para la distribución y ejecución de tareas de simulación de partículas. La versión final (ETAPA 6) implementa:

✅ **Modo manual exclusivo** - Control total sobre las tareas ejecutadas
✅ **Arquitectura robusta** - Recuperación de fallos y balanceamiento
✅ **Monitoreo completo** - Métricas y estadísticas en tiempo real
✅ **Facilidad de uso** - Herramientas intuitivas para generar tareas
✅ **Escalabilidad** - Soporte para múltiples workers distribuidos
✅ **Mantenibilidad** - Código limpio y documentación completa

**¡El sistema está listo para uso en producción!** 🚀

---

**Versión**: ETAPA 6 - Versión Final
**Fecha**: 8 de Julio, 2024
**Autor**: Sistema de Orquestación Elástica
**Estado**: ✅ Producción - Modo Manual
