# Sistema de Orquestación de Simulaciones con Docker

Este proyecto implementa un sistema distribuido para ejecutar simulaciones de partículas usando Docker y un orquestador central.

## Arquitectura

- **Orquestador**: Gestiona workers, distribuye tareas y monitorea el sistema
- **Workers**: 3 contenedores que ejecutan simulaciones
- **API REST**: Interface para controlar y monitorear el sistema

## Estructura del Proyecto

```
├── docker-compose.yml          # Configuración de servicios
├── Dockerfile                  # Imagen para workers
├── Dockerfile.orchestrator     # Imagen para orquestador
├── orchestrator.py            # Código del orquestador
├── worker_service.py          # Servicio worker
├── benchmark.py               # Simulación Python puro
├── benchmark_cython.py        # Simulación optimizada con Cython
├── configs/
│   └── tasks.yaml            # Configuración de tareas
├── scripts/
│   ├── start_system.sh       # Script de inicio (Linux/Mac)
│   ├── start_system.bat      # Script de inicio (Windows)
│   └── orchestrator_client.py # Cliente para interactuar con el API
└── requirements*.txt          # Dependencias
```

## Instalación y Uso

### Prerrequisitos

- Docker
- Docker Compose
- Python 3.10+ (para el cliente)

### Inicio Rápido

#### En Windows:
```cmd
# Ejecutar script de inicio
scripts\start_system.bat

# O manualmente:
docker-compose build
docker-compose up -d
```

#### En Linux/Mac:
```bash
# Dar permisos de ejecución
chmod +x scripts/start_system.sh

# Ejecutar script de inicio
./scripts/start_system.sh

# O manualmente:
docker-compose build
docker-compose up -d
```

### Verificar el Sistema

```bash
# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs -f orchestrator
docker-compose logs -f worker1 worker2 worker3
```

## Uso del API

### Endpoints Principales

- `GET /status` - Estado del sistema
- `GET /ping_all` - Ping a todos los workers
- `POST /execute_tasks` - Ejecutar todas las tareas
- `GET /workers` - Información de workers

### Ejemplos con curl

```bash
# Verificar estado
curl http://localhost:5000/status

# Hacer ping a workers
curl http://localhost:5000/ping_all

# Ejecutar tareas
curl -X POST http://localhost:5000/execute_tasks

# Ver información de workers
curl http://localhost:5000/workers
```

### Usando el Cliente Python

```bash
# Instalar dependencias del cliente
pip install requests

# Verificar estado
python scripts/orchestrator_client.py status

# Hacer ping
python scripts/orchestrator_client.py ping

# Ejecutar tareas
python scripts/orchestrator_client.py execute

# Monitorear sistema
python scripts/orchestrator_client.py monitor --interval 5
```

## Configuración de Tareas

Las tareas se definen en `configs/tasks.yaml`. Ejemplo:

```yaml
tasks:
  - id: "simulation_small"
    type: "benchmark"
    parameters:
      num_particulas: 100
      num_pasos: 1000
      semilla: 42
    priority: 1
    description: "Simulación pequeña"
```

### Tipos de Tareas

- `benchmark`: Simulación con Python puro
- `benchmark_cython`: Simulación optimizada con Cython

### Parámetros

- `num_particulas`: Número de partículas en la simulación
- `num_pasos`: Número de pasos de la simulación
- `semilla`: Semilla para generación aleatoria

## Monitoreo

### Health Checks

El orquestador realiza pings automáticos cada 30 segundos a todos los workers.

### Logs

Los logs se guardan en:
- Orquestador: `/app/logs/orchestrator.log` (dentro del contenedor)
- Workers: logs de Docker Compose

### Resultados

Los resultados se guardan en `/app/results/` dentro del contenedor del orquestador.

## Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un worker específico
docker-compose restart worker1

# Escalar workers
docker-compose up -d --scale worker1=2

# Parar sistema
docker-compose down

# Limpiar todo
docker-compose down -v
docker system prune -f
```

## Desarrollo y Debugging

### Ejecutar en modo desarrollo

```bash
# Con logs verbosos
docker-compose up

# Reconstruir imágenes
docker-compose build --no-cache
```

### Acceder a un contenedor

```bash
# Acceder al orquestador
docker-compose exec orchestrator bash

# Acceder a un worker
docker-compose exec worker1 bash
```

### Personalizar configuración

1. Modificar `configs/tasks.yaml` para cambiar tareas
2. Ajustar `docker-compose.yml` para cambiar puertos o recursos
3. Editar `orchestrator.py` para cambiar lógica de distribución

## Solución de Problemas

### Workers no responden

```bash
# Verificar estado de contenedores
docker-compose ps

# Reiniciar workers
docker-compose restart worker1 worker2 worker3

# Ver logs para errores
docker-compose logs worker1
```

### Orquestador no inicia

```bash
# Ver logs del orquestador
docker-compose logs orchestrator

# Verificar configuración
docker-compose config
```

### Problemas de red

```bash
# Verificar red de Docker
docker network ls
docker network inspect tarea_simulation_network
```

## Extensiones Futuras

- [ ] Balanceador de carga inteligente
- [ ] Recuperación automática de fallos
- [ ] Dashboard web
- [ ] Métricas de rendimiento
- [ ] Soporte para más tipos de simulación
- [ ] Persistencia de resultados en base de datos
