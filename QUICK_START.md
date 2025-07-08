# GUÍA DE INICIO RÁPIDO - ETAPA 6

## 🚀 Despliegue en 5 Minutos

### 1. Preparación Inicial
```bash
# Verificar sistema
python verify_etapa6.py

# Despliegue automático (Windows)
deploy_etapa6.bat

# Despliegue manual (Linux/Mac)
pip install -r requirements.txt
mkdir -p logs results
```

### 2. Configuración Básica

#### Editar .env
```bash
# IPs de workers
WORKER_01_IP=192.168.1.101
WORKER_02_IP=192.168.1.102

# Configuración ETAPA 6
TASK_DISTRIBUTION_INTERVAL=2.0
MAX_TASK_RETRIES=3
RESULTS_STORAGE_PATH=results/
```

#### Editar config_workers.json
```json
{
  "workers": [
    {
      "id": "worker1",
      "host": "192.168.1.101",
      "port": 5001,
      "capacity": 2
    },
    {
      "id": "worker2",
      "host": "192.168.1.102", 
      "port": 5001,
      "capacity": 2
    }
  ]
}
```

### 3. Ejecución

#### Máquina Maestro
```bash
# Iniciar orchestrator
python elastic_orchestrator_v6.py

# O usar script
./start_elastic_orchestrator_v6.sh
```

#### Máquinas Worker
```bash
# Worker 1
python worker_service.py --worker-id worker1 --port 5001

# Worker 2  
python worker_service.py --worker-id worker2 --port 5001

# O usar script
./start_worker.sh
```

### 4. Pruebas Básicas

#### Generar Tareas
```bash
# Tareas de prueba
python task_generator.py

# Tareas específicas
python task_generator.py --count 5 --algorithm benchmark.py
```

#### Monitorear Sistema
```bash
# Estado general
curl http://localhost:5000/stats

# Lista de tareas
curl http://localhost:5000/tasks

# Estado de workers
curl http://localhost:5000/workers
```

### 5. Verificación

#### Logs
```bash
# Orchestrator
tail -f logs/elastic_orchestrator.log

# Worker
tail -f logs/worker_service.log
```

#### Resultados
```bash
# Directorio de resultados
ls -la results/

# Historial de worker
curl http://worker-ip:5001/history
```

## 🔧 Solución de Problemas

### Worker No Responde
```bash
# Verificar conectividad
ping worker-ip
telnet worker-ip 5001

# Reiniciar worker
./start_worker.sh
```

### Tareas Fallidas
```bash
# Ver tareas fallidas
curl http://localhost:5000/tasks?status=failed

# Reiniciar orchestrator
python elastic_orchestrator_v6.py
```

### Rendimiento Bajo
```bash
# Aumentar workers
# Ajustar capacity en config_workers.json
# Usar benchmark_cython.py
```

## 📊 Comandos Útiles

```bash
# Estado completo del sistema
curl http://localhost:5000/stats | python -m json.tool

# Crear tarea personalizada
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" -d '{"algorithm": "benchmark.py", "parameters": {"NUM_PARTICULAS": 100, "NUM_PASOS": 500}, "priority": 1}'

# Exportar estadísticas
curl http://localhost:5000/stats/export > stats_export.json

# Historial de worker específico
curl http://worker-ip:5001/history | python -m json.tool
```

## 🎯 Casos de Uso

### Desarrollo
- Usar pocos workers (1-2)
- Tareas pequeñas para pruebas rápidas
- Monitoreo frecuente

### Producción
- Múltiples workers distribuidos
- Tareas de diferentes prioridades
- Monitoreo automatizado

### Benchmarking
- Usar benchmark_cython.py
- Configurar capacity alta
- Medir tiempos de ejecución

---

¿Problemas? Consultar README_ETAPA6.md para documentación completa.
