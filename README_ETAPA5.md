# 🎭 ETAPA 5: SISTEMA DE ORQUESTACIÓN ELÁSTICO

## 📋 DESCRIPCIÓN

La **ETAPA 5** implementa un **maestro elástico** con **2 memorias** (hilos) que monitorean constantemente:

### 🧠 **MEMORIAS ACTIVAS**
1. **MEMORIA 1**: Monitor de Workers (ping constante)
2. **MEMORIA 2**: Monitor de Tareas (preparación para ETAPA 6)

### ✨ **CARACTERÍSTICAS PRINCIPALES**

- **Monitoreo continuo** de workers cada 5 segundos
- **Detección automática** de workers que se conectan/desconectan
- **Estado persistente** guardado en `logs/worker_state.json`
- **Estadísticas en tiempo real** de rendimiento y conectividad
- **Recuperación automática** de workers que vuelven a conectarse
- **Interfaz de gestión** interactiva
- **Logs detallados** para debugging y análisis
- **Configuración flexible** via archivo `.env`

## 🏗️ **ARQUITECTURA**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAESTRO ELÁSTICO                             │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │   MEMORIA 1     │              │   MEMORIA 2     │          │
│  │ Worker Monitor  │              │ Task Monitor    │          │
│  │                 │              │                 │          │
│  │ • Ping continuo │              │ • Cola de tareas│          │
│  │ • Estado salud  │              │ • Balanceador   │          │
│  │ • Estadísticas  │              │ • Recuperación  │          │
│  └─────────────────┘              └─────────────────┘          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 ESTADO PERSISTENTE                        │  │
│  │           (logs/worker_state.json)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
         ┌─────────────────────────────────────────────────────────┐
         │                    WORKERS                               │
         │                                                         │
         │  ┌─────────────┐              ┌─────────────┐          │
         │  │  Worker 01  │              │  Worker 02  │          │
         │  │ 172.20.10.3 │              │ 172.20.10.9 │          │
         │  │             │              │             │          │
         │  │ • HTTP API  │              │ • HTTP API  │          │
         │  │ • Docker    │              │ • Docker    │          │
         │  │ • Benchmarks│              │ • Benchmarks│          │
         │  └─────────────┘              └─────────────┘          │
         └─────────────────────────────────────────────────────────┘
```

## 🚀 **CONFIGURACIÓN Y EJECUCIÓN**

### **1. MÁQUINA MAESTRO (Orquestador)**

#### **Archivos necesarios:**
- `elastic_orchestrator.py` - Sistema elástico principal
- `config_manager.py` - Gestor de configuración
- `.env` - Configuración del sistema
- `config_workers.json` - Configuración de workers
- `monitor_elastic.py` - Monitor en tiempo real
- `start_elastic_orchestrator.sh` - Script de inicio

#### **Configuración en `.env`:**
```bash
# IPs de los workers
WORKER_01_IP=172.20.10.3
WORKER_02_IP=172.20.10.9

# Configuración elástica
ELASTIC_PING_INTERVAL=5
ELASTIC_HEALTH_CHECK_INTERVAL=10
ELASTIC_MAX_PING_FAILURES=5
ELASTIC_HEALTH_TIMEOUT=30
```

#### **Ejecutar maestro elástico:**
```bash
# Opción 1: Script automático
./start_elastic_orchestrator.sh

# Opción 2: Ejecución directa
python3 elastic_orchestrator.py

# Opción 3: Monitor en tiempo real (ventana separada)
python3 monitor_elastic.py
```

### **2. MÁQUINAS WORKERS (172.20.10.3 y 172.20.10.9)**

#### **Archivos necesarios:**
- `worker_service.py` - Servicio HTTP del worker
- `start_worker.sh` - Script de inicio
- `benchmark.py` - Benchmark Python
- `benchmark_cython.py` - Benchmark optimizado
- `Dockerfile` - Imagen Docker
- `requirements_worker.txt` - Dependencias

#### **Ejecutar workers:**
```bash
# En cada VM worker
./start_worker.sh

# Verificar que esté funcionando
curl http://localhost:8080/ping
```

## 🎛️ **OPCIONES DE MENÚ**

### **1. Estado de workers**
- Muestra estado actual de todos los workers
- Tiempo de respuesta promedio
- Número de tareas completadas
- Estado de salud (healthy/unhealthy)

### **2. Estadísticas del sistema**
- Tiempo de actividad (uptime)
- Estadísticas de ping (total, exitosos, fallidos)
- Tasa de éxito de conectividad
- Workers descubiertos/perdidos

### **3. Ejecutar tarea**
- Seleccionar worker específico o automático
- Configurar parámetros de simulación
- Ejecutar benchmark Python o Cython

### **4. Mostrar configuración**
- Configuración actual desde `.env`
- Parámetros de workers
- Timeouts y configuración de red

### **5. Logs en tiempo real**
- Monitoreo de logs en vivo
- Actividad de ping y workers
- Errores y eventos del sistema

## 📊 **MONITOREO Y LOGS**

### **Archivos de logs:**
- `logs/elastic_orchestrator.log` - Log principal del sistema
- `logs/worker_state.json` - Estado persistente de workers
- `logs/worker_YYYYMMDD_HHMMSS.log` - Logs individuales de workers

### **Información monitoreada:**
- **Estado del worker**: active, inactive, unstable
- **Tiempo de respuesta**: promedio de últimos 10 pings
- **Fallos consecutivos**: contador de pings fallidos
- **Última conexión exitosa**: timestamp del último ping exitoso
- **Tareas completadas**: contador de benchmarks ejecutados
- **Salud del worker**: healthy/unhealthy basado en múltiples métricas

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Parámetros elásticos en `.env`:**
```bash
# Intervalo entre pings (segundos)
ELASTIC_PING_INTERVAL=5

# Intervalo de verificación de salud (segundos)
ELASTIC_HEALTH_CHECK_INTERVAL=10

# Máximo fallos antes de marcar como inactivo
ELASTIC_MAX_PING_FAILURES=5

# Timeout para considerar worker unhealthy (segundos)
ELASTIC_HEALTH_TIMEOUT=30
```

### **Configuración de red:**
```bash
# Timeout para conexiones HTTP
HTTP_TIMEOUT=10

# Timeout para ejecución de tareas
TASK_TIMEOUT=60
```

## 🧪 **PRUEBAS Y VERIFICACIÓN**

### **1. Verificar conectividad:**
```bash
# Ping a workers
ping 172.20.10.3
ping 172.20.10.9

# Verificar servicios HTTP
curl http://172.20.10.3:8080/ping
curl http://172.20.10.9:8080/ping
```

### **2. Probar elasticidad:**
```bash
# Detener un worker
# En worker: Ctrl+C para detener worker_service.py

# Verificar en maestro:
# - Estado cambia a "inactive"
# - Fallos consecutivos aumentan
# - Worker marcado como unhealthy

# Reiniciar worker
# En worker: ./start_worker.sh

# Verificar en maestro:
# - Estado cambia a "active"
# - Fallos consecutivos se resetean
# - Worker marcado como healthy
```

### **3. Verificar estado persistente:**
```bash
# Ver estado actual
cat logs/worker_state.json

# Verificar logs
tail -f logs/elastic_orchestrator.log
```

## 🔄 **FLUJO DE TRABAJO**

### **1. Inicio del sistema:**
1. Configurar IPs en `.env`
2. Iniciar workers en cada VM
3. Iniciar maestro elástico
4. Verificar conectividad automática

### **2. Monitoreo continuo:**
1. **MEMORIA 1** hace ping cada 5 segundos
2. Actualiza estado y estadísticas
3. Detecta workers que se conectan/desconectan
4. Guarda estado persistente

### **3. Gestión de tareas:**
1. **MEMORIA 2** prepara gestión de tareas
2. Encuentra mejor worker disponible
3. Ejecuta benchmark seleccionado
4. Actualiza estadísticas de rendimiento

## 📈 **MÉTRICAS Y ESTADÍSTICAS**

### **Por worker:**
- Estado actual (active/inactive/unstable)
- Tiempo de respuesta promedio
- Fallos consecutivos
- Última conexión exitosa
- Tareas completadas
- Estado de salud

### **Del sistema:**
- Tiempo de actividad (uptime)
- Pings totales realizados
- Pings exitosos/fallidos
- Tasa de éxito de conectividad
- Workers descubiertos/perdidos

## 🚨 **TROUBLESHOOTING**

### **Worker no responde:**
```bash
# Verificar estado del worker
ssh user@172.20.10.3
ps aux | grep worker_service.py

# Reiniciar worker
./start_worker.sh
```

### **Problemas de conectividad:**
```bash
# Verificar red
ping 172.20.10.3

# Verificar puerto
telnet 172.20.10.3 8080
```

### **Logs de error:**
```bash
# Ver logs del maestro
tail -f logs/elastic_orchestrator.log

# Ver logs de worker
tail -f logs/worker_*.log
```

## 🎯 **DIFERENCIAS CON ETAPA 4**

### **ETAPA 4:**
- Orquestador simple con ping manual
- Ejecución de tareas bajo demanda
- Sin monitoreo continuo
- Estado no persistente

### **ETAPA 5:**
- **Maestro elástico** con 2 memorias
- **Monitoreo continuo** automático
- **Estado persistente** en tiempo real
- **Detección automática** de workers
- **Estadísticas avanzadas** de rendimiento
- **Recuperación automática** de fallos

## 🔮 **PREPARACIÓN PARA ETAPA 6**

La **MEMORIA 2** está preparada para implementar en ETAPA 6:
- **Cola de tareas** distribuida
- **Balanceamiento de carga** automático
- **Recuperación de tareas** fallidas
- **Priorización** de tareas
- **Distribución inteligente** basada en rendimiento

---

## 🎉 **RESUMEN**

La **ETAPA 5** transforma el sistema en un **orquestador elástico** que:

✅ **Monitorea continuamente** todos los workers  
✅ **Detecta automáticamente** cambios en la topología  
✅ **Mantiene estado persistente** de la infraestructura  
✅ **Proporciona estadísticas** en tiempo real  
✅ **Se recupera automáticamente** de fallos  
✅ **Prepara el camino** para distribución avanzada de tareas en ETAPA 6

**¡El sistema ahora es verdaderamente elástico y auto-gestionado!** 🚀
