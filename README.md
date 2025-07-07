# Sistema de Orquestación de Simulaciones con Docker

Este proyecto implementa un sistema distribuido para ejecutar simulaciones de partículas usando Docker y un orquestador central que puede funcionar tanto localmente como distribuido en múltiples máquinas virtuales.

## 🏗️ Arquitectura

### **Modo Local (Todo en una máquina):**
- **Orquestador**: Gestiona workers localmente
- **Workers**: 3 contenedores en la misma máquina
- **API REST**: Interface para controlar y monitorear

### **Modo Distribuido (Múltiples máquinas):**
- **PC Principal**: Ejecuta orquestador
- **VM1, VM2, VM3**: Cada una ejecuta un worker
- **Comunicación**: API REST entre máquinas via red

## 📁 Estructura del Proyecto

```
├── docker-compose.yml          # Configuración de servicios locales
├── Dockerfile.worker           # Imagen para workers
├── Dockerfile.orchestrator     # Imagen para orquestador
├── orchestrator.py            # Código del orquestador
├── worker_service.py          # Servicio worker
├── benchmark.py               # Simulación Python puro
├── benchmark_cython.py        # Simulación optimizada con Cython
├── configs/
│   ├── tasks.yaml            # Configuración de tareas
│   └── network.yaml          # Configuración de red distribuida
├── scripts/
│   ├── build_and_export.bat  # Construir y exportar imágenes TAR
│   ├── create_vm_packages.bat # Crear paquetes para VMs
│   ├── run_orchestrator.bat  # Ejecutar orquestador
│   ├── run_worker*.bat       # Ejecutar workers específicos
│   ├── verify_system.bat     # Verificar sistema completo
│   └── orchestrator_client.py # Cliente para interactuar con el API
├── VM_Packages/               # Paquetes generados para VMs
├── INSTALACION_DISTRIBUIDA.md # Guía completa de instalación distribuida
└── requirements*.txt          # Dependencias
```

## 🚀 Instalación y Uso

### 📋 Prerrequisitos

- Docker
- Docker Compose
- Python 3.10+ (para el cliente)

### ⚡ Inicio Rápido - Modo Local

#### En Windows:
```cmd
# Ejecutar script de inicio
scripts\start_system.bat

# O manualmente:
docker-compose build
docker-compose up -d
```

### 🌐 Instalación Distribuida (Múltiples VMs)

Para configurar el sistema distribuido con workers en múltiples máquinas virtuales, sigue la guía completa:

📖 **[GUÍA COMPLETA DE INSTALACIÓN DISTRIBUIDA](INSTALACION_DISTRIBUIDA.md)**

#### Resumen rápido:

**1. En tu PC Principal:**
```cmd
# Construir y exportar imágenes TAR
scripts\build_and_export.bat

# Crear paquetes para VMs
scripts\create_vm_packages.bat

# Ejecutar orquestador
scripts\run_orchestrator.bat
```

**2. En cada VM:**
```cmd
# Cargar imagen Docker
load_images.bat

# Ejecutar worker correspondiente
run_worker1.bat  # VM1
run_worker2.bat  # VM2
run_worker3.bat  # VM3
```

**3. Verificar sistema:**
```cmd
scripts\verify_system.bat
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
