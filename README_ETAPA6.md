# ETAPA 6: SISTEMA DE ORQUESTACIÓN CON COLA DE TAREAS DISTRIBUIDA - MODO MANUAL

## Descripción General

La ETAPA 6 implementa un sistema de orquestación elástica con cola de tareas distribuida que permite:

- **Cola de tareas manual**: Gestión de tareas cargadas manualmente desde archivos JSON
- **Distribución automática**: Asignación inteligente de tareas a workers disponibles
- **Almacenamiento de resultados**: Persistencia de tiempos de ejecución y resultados
- **Balanceamiento de carga**: Distribución eficiente basada en capacidad de workers
- **Recuperación de fallos**: Reintentos automáticos para tareas fallidas
- **Métricas de rendimiento**: Tracking detallado por worker y tarea
- **Ingreso manual de tareas**: Solo procesa archivos JSON agregados manualmente al directorio `task_queues/`

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Orchestrator  │    │     Worker 1    │    │     Worker 2    │
│   (Maestro)     │    │                 │    │                 │
│                 │    │                 │    │                 │
│ • Task Queue    │◄──►│ • Task Executor │    │ • Task Executor │
│ • Load Balancer │    │ • Results Store │    │ • Results Store │
│ • Fault Recovery│    │ • Performance   │    │ • Performance   │
│ • Statistics    │    │   Metrics       │    │   Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Componentes Principales

### 1. Orchestrator (Maestro)
- **Archivo**: `elastic_orchestrator_v6.py`
- **Puerto**: 5000
- **Función**: Gestión de la cola de tareas y coordinación de workers
- **Modo**: Manual - solo procesa archivos JSON colocados manualmente

### 2. Workers (Trabajadores)
- **Archivo**: `worker_service.py`
- **Puerto**: 5001, 5002, 5003, etc.
- **Función**: Ejecución de tareas y reporte de resultados

### 3. Manual Task Generator
- **Archivo**: `manual_task_generator.py`
- **Función**: Herramienta para generar archivos JSON con tareas para ingreso manual

### 4. Task Queue Directory
- **Directorio**: `task_queues/`
- **Función**: Directorio monitoreado para archivos JSON con tareas manuales

## Configuración del Sistema

### Variables de Entorno (.env)
```bash
# ETAPA 6: Configuración de Cola de Tareas - MODO MANUAL
TASK_DISTRIBUTION_INTERVAL=2.0    # Intervalo de distribución de tareas
MAX_TASK_RETRIES=3                # Máximo número de reintentos
RESULTS_STORAGE_PATH=results/     # Directorio para almacenar resultados
TASK_HISTORY_SIZE=1000           # Tamaño del historial de tareas
WORKER_TIMEOUT=300               # Timeout para workers (segundos)
LOAD_BALANCING_ALGORITHM=round_robin  # Algoritmo de balanceamiento
PERFORMANCE_MONITORING=true      # Habilitar monitoreo de rendimiento
MANUAL_MODE=true                 # Modo manual activado (sin generación automática)
```

### Configuración de Workers (config_workers.json)
```json
{
  "workers": [
    {
      "id": "worker1",
      "host": "192.168.1.100",
      "port": 5001,
      "capacity": 2,
      "algorithms": ["python", "cython"]
    },
    {
      "id": "worker2", 
      "host": "192.168.1.101",
      "port": 5001,
      "capacity": 4,
      "algorithms": ["python", "cython"]
    }
  ]
}
```

## Despliegue en Máquinas Virtuales

### Máquina del Orchestrator (Maestro)

#### 1. Preparación del Entorno
```bash
# Clonar el repositorio
git clone <repository-url>
cd TAREA

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p logs results
```

#### 2. Configuración
```bash
# Configurar workers en config_workers.json
# Ajustar variables en .env según necesidades

# Verificar configuración
python config_manager.py
```

#### 3. Iniciar el Orchestrator

**Modo Manual - Solo Archivos JSON**
```bash
# Iniciar el orchestrator en modo manual
python elastic_orchestrator_v6.py

# El sistema monitorea automáticamente el directorio task_queues/
# No genera tareas automáticamente
```

#### 4. Verificar Estado
```bash
# Verificar que el orchestrator esté funcionando
curl http://localhost:5000/stats

# Verificar workers registrados
curl http://localhost:5000/workers
```

### Máquinas Worker (Trabajadores)

#### 1. Preparación del Entorno
```bash
# Clonar el repositorio
git clone <repository-url>
cd TAREA

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias del worker
pip install -r requirements_worker.txt

# Crear directorios necesarios
mkdir -p logs results
```

#### 2. Configuración
```bash
# Configurar ID y puerto del worker
export WORKER_ID=worker1
export WORKER_PORT=5001

# En Windows:
set WORKER_ID=worker1
set WORKER_PORT=5001
```

#### 3. Iniciar Worker
```bash
# Opción 1: Script de inicio (recomendado)
./start_worker.sh

# Opción 2: Directamente
python worker_service.py --worker-id worker1 --port 5001
```

#### 4. Verificar Estado
```bash
# Verificar que el worker esté funcionando
curl http://localhost:5001/status

# Verificar historial de tareas
curl http://localhost:5001/history
```

## Uso del Sistema - MODO MANUAL

### 1. Crear Tareas Manualmente

#### Generar Archivos JSON de Tareas
```bash
# Usar el generador manual de tareas
python manual_task_generator.py

# Esto te permite crear archivos JSON con tareas personalizadas
# El archivo se guarda en task_queues/ y es procesado automáticamente
```

#### Estructura de Archivo JSON de Tareas
```json
{
  "metadata": {
    "creation_date": "2024-01-15",
    "description": "Tareas de simulación de partículas",
    "total_tasks": 5,
    "created_by": "Manual Task Generator"
  },
  "tasks": [
    {
      "task_id": "task_001",
      "algorithm": "python",
      "parameters": {
        "num_particles": 100,
        "num_steps": 500,
        "seed": 123
      },
      "priority": "high",
      "description": "Simulación Python - 100 partículas"
    },
    {
      "task_id": "task_002",
      "algorithm": "cython",
      "parameters": {
        "num_particles": 200,
        "num_steps": 800,
        "seed": 456
      },
      "priority": "medium",
      "description": "Simulación Cython - 200 partículas"
    }
  ]
}
```

#### Usar Archivos de Ejemplo
```bash
# Copiar archivo de ejemplo al directorio de colas
cp tareas_manuales_ejemplo.json task_queues/

# El orchestrator procesará el archivo automáticamente
# El archivo se moverá a task_queues/processed/ después del procesamiento
```

### 2. Workflow Manual de Tareas

#### Paso 1: Crear Archivo JSON
```bash
# Opción 1: Usar el generador manual
python manual_task_generator.py

# Opción 2: Copiar archivo de ejemplo
cp tareas_manuales_ejemplo.json task_queues/mi_lote_tareas.json

# Opción 3: Crear manualmente siguiendo la estructura JSON
```

#### Paso 2: Verificar Procesamiento
```bash
# Verificar que el archivo fue procesado
ls task_queues/processed/

# Ver estadísticas del orchestrator
curl http://localhost:5000/stats
```

#### Paso 3: Monitorear Ejecución
```bash
# Ver tareas en cola
curl http://localhost:5000/tasks

# Ver estado de workers
curl http://localhost:5000/workers
```

### 3. Agregar Más Tareas

#### Agregar Nuevas Tareas Durante Ejecución
```bash
# Simplemente copia/crea nuevos archivos JSON en task_queues/
cp nuevas_tareas.json task_queues/

# El orchestrator las detectará automáticamente
```

#### Monitorear Directorio de Colas
```bash
# Ver archivos pendientes
ls task_queues/

# Ver archivos procesados
ls task_queues/processed/
```

### 2. Monitorear el Sistema

#### Estado del Orchestrator
```bash
# Estadísticas generales
curl http://localhost:5000/stats

# Lista de tareas
curl http://localhost:5000/tasks

# Estado de workers
curl http://localhost:5000/workers
```

#### Estado de Workers
```bash
# Estado del worker
curl http://worker-host:5001/status

# Historial de tareas del worker
curl http://worker-host:5001/history

# Métricas de rendimiento
curl http://worker-host:5001/metrics
```

### 3. Resultados y Análisis

#### Estructura de Resultados
```
results/
├── task_results_20240115_103000.json   # Resultados de tareas ejecutadas
├── task_results_20240115_104000.json   # Resultados por timestamp
└── orchestrator_stats.json             # Estadísticas del orchestrator

task_queues/                            # Directorio de colas manuales
├── tareas_manuales_ejemplo.json       # Archivo de ejemplo listo para usar
├── mi_lote_tareas.json                 # Archivo personalizado (pendiente)
└── processed/                          # Archivos procesados
    ├── 20240115_103000_tareas_manuales_ejemplo.json
    └── 20240115_104000_mi_lote_tareas.json

logs/
├── elastic_orchestrator.log           # Logs del orchestrator
└── worker_state.json                  # Estado de workers
```

#### Ejemplo de Resultado de Tarea
```json
{
  "task_id": "task_001",
  "algorithm": "python",
  "parameters": {
    "num_particles": 100,
    "num_steps": 500,
    "seed": 123
  },
  "execution_time": 45.2,
  "result": {
    "status": "completed",
    "metrics": {
      "particles_processed": 100,
      "steps_completed": 500,
      "memory_used": "45.2 MB"
    },
    "output": "Simulación completada exitosamente"
  },
  "worker_id": "worker1",
  "completed_at": "2024-01-15T10:30:00",
  "priority": "high"
}
```

## Nuevas Funcionalidades de ETAPA 6

### 1. Cola de Tareas Distribuida - MODO MANUAL
- **Priorización**: Tareas con diferentes prioridades (high, medium, low)
- **Persistencia**: Almacenamiento de tareas en disco
- **Balanceamiento**: Distribución inteligente basada en capacidad de workers
- **Ingreso Manual**: Solo procesa archivos JSON colocados manualmente

### 2. Procesamiento Manual de Archivos JSON
- **Monitoreo de Directorio**: Revisa automáticamente el directorio `task_queues/`
- **Carga desde Archivos**: Procesa archivos JSON con listas de tareas
- **Archivos Procesados**: Mueve archivos procesados a `processed/`
- **Sin Generación Automática**: No crea tareas automáticamente

### 3. Herramientas de Generación Manual
- **Manual Task Generator**: Herramienta interactiva para crear archivos JSON
- **Archivos de Ejemplo**: Incluye `tareas_manuales_ejemplo.json` listo para usar
- **Estructuras Validadas**: Formato JSON verificado y documentado

### 4. Recuperación de Fallos
- **Reintentos**: Reintento automático de tareas fallidas
- **Timeout**: Detección de workers no responsivos
- **Redistribución**: Reasignación de tareas a otros workers

### 5. Monitoreo de Rendimiento
- **Métricas por Worker**: Tiempo promedio, tareas completadas, etc.
- **Métricas por Tarea**: Tiempo de ejecución, recursos utilizados
- **Estadísticas Globales**: Throughput, latencia, utilización

### 6. Sistema de Monitoreo Continuo
- **Monitor de Workers**: Ping constante a workers registrados
- **Monitor de Tareas**: Distribución automática de tareas en cola
- **Monitor de Archivos**: Detección automática de nuevos archivos JSON

## Endpoints API

### Orchestrator (Puerto 5000)

#### Tareas
- `GET /tasks` - Listar todas las tareas
- `GET /tasks/{task_id}` - Obtener tarea específica
- `DELETE /tasks/{task_id}` - Cancelar tarea
- `POST /tasks` - Crear nueva tarea (solo vía API, no recomendado en modo manual)

#### Workers
- `GET /workers` - Listar workers registrados
- `GET /workers/{worker_id}` - Información de worker específico

#### Estadísticas
- `GET /stats` - Estadísticas generales del orchestrator
- `GET /stats/performance` - Métricas de rendimiento
- `GET /health` - Estado de salud del sistema

### Worker (Puerto 5001+)

#### Estado
- `GET /status` - Estado actual del worker
- `GET /health` - Verificación de salud
- `GET /metrics` - Métricas de rendimiento

#### Tareas
- `POST /execute` - Ejecutar tarea (usado internamente por orchestrator)
- `GET /history` - Historial de tareas ejecutadas
- `GET /current` - Tarea actual en ejecución

## Monitoreo y Troubleshooting

### Logs del Sistema
```bash
# Logs del orchestrator
tail -f logs/elastic_orchestrator.log

# Logs del worker
tail -f logs/worker_service.log
```

### Problemas Comunes

#### 1. No se Procesan Archivos JSON
```bash
# Verificar que el archivo esté en el directorio correcto
ls task_queues/

# Verificar formato JSON
python -m json.tool task_queues/mi_archivo.json

# Revisar logs del orchestrator
tail -f logs/elastic_orchestrator.log
```

#### 2. Worker No Responde
```bash
# Verificar conectividad
curl http://worker-host:5001/health

# Revisar logs
tail -f logs/worker_service.log

# Reiniciar worker
./start_worker.sh
```

#### 3. Tareas Fallidas
```bash
# Ver tareas fallidas
curl http://localhost:5000/tasks?status=failed

# Ver detalles de error
curl http://localhost:5000/tasks/{task_id}
```

#### 4. Archivos JSON Malformados
```bash
# Validar formato JSON
python -c "import json; print(json.load(open('task_queues/mi_archivo.json')))"

# Usar el generador manual para crear archivos válidos
python manual_task_generator.py
```

## Pruebas y Validación

### 1. Pruebas Básicas
```bash
# Prueba de conectividad
python test_communication.py

# Prueba con archivo de ejemplo
cp tareas_manuales_ejemplo.json task_queues/
# Monitorear en http://localhost:5000/stats
```

### 2. Pruebas de Carga Manual
```bash
# Generar múltiples archivos de tareas
python manual_task_generator.py  # Ejecutar varias veces

# Verificar procesamiento
ls task_queues/processed/
```

### 3. Pruebas de Validación
```bash
# Validar formato de archivos JSON
python -m json.tool tareas_manuales_ejemplo.json

# Probar diferentes tipos de tareas
python manual_task_generator.py
```

## Escalabilidad

### Agregar Nuevos Workers
1. Configurar nueva VM
2. Instalar dependencias
3. Agregar configuración en `config_workers.json`
4. Iniciar worker con ID único
5. Verificar registro en orchestrator

### Optimización de Rendimiento
- Ajustar `TASK_DISTRIBUTION_INTERVAL` para mayor throughput
- Incrementar `capacity` de workers con más recursos
- Usar algoritmo `cython` para mejor rendimiento
- Configurar `LOAD_BALANCING_ALGORITHM` apropiado
- Crear lotes de tareas más grandes en archivos JSON

## Desarrollo y Extensiones

### Agregar Nuevos Algoritmos
1. Implementar algoritmo en `simulacion_partic.py`
2. Agregar soporte en `worker_service.py`
3. Actualizar configuración de workers
4. Probar con archivos JSON de tareas

### Crear Nuevos Tipos de Tareas
1. Definir estructura en archivo JSON
2. Implementar validación en orchestrator
3. Agregar soporte en workers
4. Documentar formato en README

### Métricas Personalizadas
- Extender resultado de tareas en JSON
- Modificar endpoints de estadísticas
- Actualizar almacenamiento de resultados
- Crear nuevos campos en `manual_task_generator.py`

## Archivos de Ejemplo Incluidos

### `tareas_manuales_ejemplo.json`
- Archivo listo para usar con 10 tareas variadas
- Incluye tareas Python y Cython
- Diferentes prioridades y parámetros
- Simplemente copiarlo a `task_queues/` para procesamiento

### `manual_task_generator.py`
- Herramienta interactiva para crear archivos JSON
- Validación automática de formato
- Opciones personalizables
- Guía paso a paso

## Contacto y Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
- Revisar logs del sistema
- Verificar configuración de red
- Consultar este README para troubleshooting
- Contactar al equipo de desarrollo

---

**Versión**: ETAPA 6 - Modo Manual
**Fecha**: Julio 2024
**Autor**: Sistema de Orquestación Elástica - Ingreso Manual de Tareas

**Cambios en esta versión**:
- ✅ Implementado modo manual exclusivo
- ✅ Eliminada generación automática de tareas
- ✅ Monitoreo automático de directorio `task_queues/`
- ✅ Herramienta `manual_task_generator.py`
- ✅ Archivo de ejemplo `tareas_manuales_ejemplo.json`
- ✅ Documentación completa del workflow manual
- ✅ Procesamiento automático de archivos JSON
- ✅ Movimiento de archivos a `processed/` después de carga
