# 🔗 ETAPA 4: SISTEMA DE COMUNICACIÓN WORKER - README

## 📋 **RESUMEN DE LA ETAPA**

Esta etapa crea el **sistema de comunicación** entre el **orquestador** (tu computador principal) y los **workers** (2 máquinas virtuales) para ejecutar simulaciones de partículas de forma distribuida.

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

```
┌─────────────────────────────────────────────────────────────┐
│                    🖥️  ORQUESTADOR                          │
│               (Tu Computador Principal)                     │
│                                                             │
│  ┌─────────────────┐  HTTP/REST  ┌─────────────────────────┐│
│  │ orchestrator.py │ ◄──────────► │   Gestión de Tareas     ││
│  └─────────────────┘              └─────────────────────────┘│
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  🖥️ WORKER 1    │ │  🖥️ WORKER 2    │ │  Futuras VMs    │
    │ 192.168.1.93    │ │ 192.168.1.155   │ │  (Escalable)    │
    │                 │ │                 │ │                 │
    │ worker_service  │ │ worker_service  │ │ worker_service  │
    │ Docker Engine   │ │ Docker Engine   │ │ Docker Engine   │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 🎯 **OBJETIVOS DE LA ETAPA**

✅ **Crear servicio worker** para recibir y ejecutar tareas  
✅ **Implementar comunicación HTTP** entre orquestador y workers  
✅ **Sistema de ping** para verificar estado de VMs  
✅ **Ejecutar benchmarks remotamente** con parámetros personalizados  
✅ **Dockerizar worker service** para fácil despliegue  
✅ **Probar comunicación** en red local  

---

## 📁 **ARCHIVOS CREADOS**

### **🔧 En el Orquestador (Tu computador)**
- ✅ `orchestrator.py` - Gestiona workers y distribuye tareas con interfaz interactiva
- ✅ `config_workers.json` - Configuración de IPs de workers (192.168.1.93, 192.168.1.155)
- ✅ `test_communication.py` - Suite completa de pruebas de conectividad

### **🖥️ En cada Worker VM (192.168.1.93 y 192.168.1.155)**
- ✅ `worker_service.py` - Servicio HTTP que recibe tareas Flask
- ✅ `requirements_worker.txt` - Dependencias específicas del worker
- ✅ `Dockerfile.worker` - Container del worker service
- ✅ `start_worker.sh` - Script automatizado para iniciar el servicio
- ✅ `start_worker.bat` - Script para Windows (testing local)

### **📦 Sistema de Distribución**
- ✅ `package_project.sh` - Script actualizado para ETAPA 4 con todos los archivos

---

## 🚀 **PASO A PASO DETALLADO**

### **📦 PASO 1: Empaquetar y Transferir a VMs**

#### **1.1 - En tu computador principal, crear TAR actualizado:**

```bash
# Crear paquete con todos los archivos de ETAPA 4
./package_project.sh
```

Este comando creará un archivo `particle-simulation-ETAPA4-YYYYMMDD-HHMMSS.tar.gz` que incluye:
- 📋 Benchmarks (benchmark.py, benchmark_cython.py)
- 🎭 Orquestador (orchestrator.py, test_communication.py, config_workers.json)
- 🖥️ Worker (worker_service.py, start_worker.sh, requirements_worker.txt)
- 🐳 Docker (Dockerfile, Dockerfile.worker)
- 📚 Documentación (README_ETAPA2.md, README_ETAPA4.md)

#### **1.2 - Transferir a las VMs:**

```bash
# Copiar a Worker 1
scp particle-simulation-ETAPA4-*.tar.gz usuario@192.168.1.93:/home/usuario/

# Copiar a Worker 2  
scp particle-simulation-ETAPA4-*.tar.gz usuario@192.168.1.155:/home/usuario/
```

### **📋 PASO 2: Configurar cada VM (192.168.1.93 y 192.168.1.155)**

#### **2.1 - En cada VM, extraer archivos:**

```bash
# Conectar a la VM
ssh usuario@192.168.1.93  # o 192.168.1.155

# Extraer proyecto
tar -xzf particle-simulation-ETAPA4-*.tar.gz
cd TAREA/

# Hacer ejecutables los scripts
chmod +x *.sh
```

#### **2.2 - Instalar dependencias:**

```bash
# Instalar dependencias Python
pip3 install flask==2.3.3 requests==2.31.0

# O usar requirements
pip3 install -r requirements_worker.txt
```

#### **2.3 - Construir imagen Docker:**

```bash
# Construir imagen de simulación
docker build -t particle-simulation:latest .

# Verificar imagen creada
docker images | grep particle-simulation
```

#### **2.4 - Iniciar Worker Service:**

```bash
# Iniciar worker automáticamente
./start_worker.sh

# O manualmente
export WORKER_ID=worker-01  # o worker-02
python3 worker_service.py
```

### **📋 PASO 3: Configurar Orquestador (Tu computador)**

#### **3.1 - Instalar dependencias:**

```bash
pip install requests
```

#### **3.2 - Verificar configuración de workers:**

El archivo `config_workers.json` ya está configurado con las IPs correctas:
- Worker 1: 192.168.1.93:8080
- Worker 2: 192.168.1.155:8080

#### **3.3 - Probar comunicación:**

```bash
# Prueba rápida de conectividad
python test_communication.py

# Usar orquestador completo
python orchestrator.py
```

---

## 🔧 **INSTALACIÓN Y CONFIGURACIÓN**

### **� Flujo Completo de Instalación:**

#### **1. En tu computador (Orquestador):**
```bash
# Empaquetar proyecto actualizado
./package_project.sh

# Instalar dependencias
pip install requests

# Transferir a VMs
scp particle-simulation-ETAPA4-*.tar.gz usuario@192.168.1.93:/home/usuario/
scp particle-simulation-ETAPA4-*.tar.gz usuario@192.168.1.155:/home/usuario/
```

#### **2. En cada VM (Configuración automática):**
```bash
# Conectar y extraer
ssh usuario@192.168.1.93  # Repetir para 192.168.1.155
tar -xzf particle-simulation-ETAPA4-*.tar.gz
cd TAREA/

# Configuración automática
chmod +x start_worker.sh
./start_worker.sh
```

El script `start_worker.sh` automaticamente:
- ✅ Detecta la IP y asigna Worker ID
- ✅ Verifica Docker 
- ✅ Instala dependencias Python
- ✅ Construye imagen si es necesario
- ✅ Inicia el worker service

#### **3. Verificar funcionamiento:**
```bash
# En el orquestador
python test_communication.py
python orchestrator.py
```

---

## 🧪 **PRUEBAS DE FUNCIONAMIENTO**

### **1. Pruebas automatizadas desde el orquestador:**

```bash
# Suite completa de pruebas
python test_communication.py

# Orquestador interactivo
python orchestrator.py
```

### **2. Pruebas manuales de endpoints:**

```bash
# Ping directo a workers
curl http://192.168.1.93:8080/ping
curl http://192.168.1.155:8080/ping

# Status detallado
curl http://192.168.1.93:8080/status

# Ejecución de tarea
curl -X POST http://192.168.1.93:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "benchmark": "benchmark.py",
    "params": {
      "NUM_PARTICULAS": 100,
      "NUM_PASOS": 500,
      "SEMILLA": 42
    }
  }'
```

### **3. Verificaciones del sistema:**

- ✅ **Workers responden al ping** en <5 segundos
- ✅ **Ejecutan tareas remotamente** sin errores
- ✅ **Retornan métricas correctas** (colisiones, tiempo)
- ✅ **Manejan timeouts** apropiadamente
- ✅ **Identificación automática** funciona por IP

---

## ✨ **CARACTERÍSTICAS IMPLEMENTADAS**

### **🎭 Sistema de Orquestación:**
- ✅ **Interfaz interactiva** con menú de opciones
- ✅ **Ping automático** para verificar VMs activas
- ✅ **Mensaje "NO HAY MÁQUINAS ACTIVAS"** cuando corresponde
- ✅ **Gestión inteligente** de workers disponibles
- ✅ **Demo automático** del sistema completo

### **🖥️ Worker Service:**
- ✅ **Identificación automática** por IP (worker-01, worker-02)
- ✅ **Endpoints REST** completos (/ping, /execute, /status, /health)
- ✅ **Ejecución de ambos benchmarks** (Python y Cython)
- ✅ **Parsing de métricas** automático (colisiones, tiempo)
- ✅ **Manejo robusto de errores** y timeouts

### **🔗 Comunicación:**
- ✅ **Protocolo HTTP/REST** estándar
- ✅ **Timeout configurables** para operaciones
- ✅ **Recolección de métricas** detalladas
- ✅ **Logging distribuido** con timestamps

### **📦 Sistema de Distribución:**
- ✅ **TAR actualizado** con todos los archivos ETAPA 4
- ✅ **Scripts de automatización** multiplataforma
- ✅ **Configuración automática** de workers
- ✅ **Verificaciones de dependencias** integradas

---

## ✅ **VERIFICACIÓN DE ÉXITO**

Para confirmar que la ETAPA 4 funciona correctamente:

1. ✅ **TAR actualizado** se crea con todos los archivos necesarios
2. ✅ **Workers se identifican automáticamente** por IP
3. ✅ **Responden al ping** desde el orquestador (<5 segundos)
4. ✅ **Ejecutan ambos benchmarks** (Python y Cython) remotamente
5. ✅ **Retornan métricas correctas** (colisiones, tiempo de ejecución)
6. ✅ **Manejan errores apropiadamente** (timeouts, Docker no disponible)
7. ✅ **Orquestador muestra "NO HAY MÁQUINAS ACTIVAS"** cuando corresponde
8. ✅ **Sistema completo** funciona end-to-end

### **🔍 Comando de verificación rápida:**
```bash
python test_communication.py
```

Este comando ejecutará una suite completa de pruebas y confirmará que todo el sistema está funcionando.

---

## 🚀 **PRÓXIMOS PASOS (ETAPA 5)**

1. **Crear sistema de cola** de tareas
2. **Implementar balanceador** de carga
3. **Gestión de archivos** de tareas múltiples
4. **Sistema de reintento** automático
5. **Dashboard de monitoreo** en tiempo real

---

**🎉 ETAPA 4: COMUNICACIÓN WORKER LISTA PARA IMPLEMENTAR 🎉**
