# 🔧 GESTIÓN DE CONFIGURACIÓN CON .ENV

Este sistema ahora utiliza un archivo `.env` para manejar toda la configuración importante, lo que facilita el mantenimiento y despliegue.

## 📁 **ARCHIVOS DE CONFIGURACIÓN**

### `.env` - Configuración principal
Contiene todas las variables de configuración del sistema:
- **Workers**: IPs, puertos, IDs
- **Docker**: Imagen, tag
- **Timeouts**: HTTP, tareas
- **Simulación**: Parámetros por defecto
- **Logging**: Configuración de logs
- **Debug**: Modo debug y verbose

### `config_manager.py` - Gestor de configuración
Módulo Python que lee y procesa el archivo `.env`:
- Carga variables del archivo `.env`
- Convierte tipos de datos automáticamente
- Genera configuración para workers
- Maneja valores por defecto

### `config_workers.json` - Respaldo JSON
Archivo JSON generado automáticamente desde `.env` para compatibilidad.

## 🚀 **CONFIGURACIÓN INICIAL**

### 1. **Editar el archivo `.env`**
```bash
# Editar las IPs de tus workers
nano .env

# Ejemplo de configuración:
WORKER_01_IP=192.168.1.93
WORKER_02_IP=192.168.1.155
```

### 2. **Generar archivo JSON**
```bash
python3 generate_config.py
```

### 3. **Verificar configuración**
```bash
python3 config_manager.py
```

## 📋 **VARIABLES PRINCIPALES**

### **Workers**
```env
WORKER_01_ID=worker-01
WORKER_01_IP=192.168.1.93
WORKER_01_PORT=8080

WORKER_02_ID=worker-02
WORKER_02_IP=192.168.1.155
WORKER_02_PORT=8080
```

### **Docker**
```env
DOCKER_IMAGE_NAME=particle-simulation
DOCKER_IMAGE_TAG=latest
```

### **Timeouts**
```env
HTTP_TIMEOUT=10
TASK_TIMEOUT=60
```

### **Simulación**
```env
DEFAULT_NUM_PARTICLES=100
DEFAULT_NUM_STEPS=500
DEFAULT_SEED=42
```

### **Modo Debug**
```env
DEBUG_MODE=false
VERBOSE_OUTPUT=true
```

## 🛠️ **SCRIPTS ÚTILES**

### **generate_config.py**
Genera `config_workers.json` desde `.env`
```bash
python3 generate_config.py
```

### **config_manager.py**
Prueba y muestra la configuración actual
```bash
python3 config_manager.py
```

## 📊 **FUNCIONES MEJORADAS**

### **Orquestador**
- ✅ Carga configuración desde `.env`
- ✅ Valores por defecto inteligentes
- ✅ Modo debug y verbose
- ✅ Recarga de configuración en tiempo real
- ✅ Timeouts configurables

### **Worker Service**
- ✅ Detección automática de configuración
- ✅ Logging mejorado
- ✅ Modo debug con información detallada
- ✅ Configuración de imagen Docker desde `.env`

## 🔄 **RECARGA DE CONFIGURACIÓN**

### **Sin reiniciar**
```bash
# En el menú del orquestador
5. Recargar configuración
```

### **Con reinicio**
```bash
# Reiniciar orchestrator
python3 orchestrator.py

# Reiniciar worker service
./start_worker.sh
```

## 🐛 **MODO DEBUG**

### **Activar debug en .env**
```env
DEBUG_MODE=true
VERBOSE_OUTPUT=true
```

### **Información adicional**
- Comandos Docker ejecutados
- Errores detallados
- Timestamps de todas las operaciones
- Información de red y conectividad

## 📝 **LOGGING**

### **Archivos de log**
```env
LOG_FILE=logs/orchestrator.log
WORKER_LOG_DIR=logs
```

### **Niveles de log**
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🔧 **PERSONALIZACIÓN**

### **Agregar nuevo worker**
1. Editar `.env`:
```env
WORKER_03_ID=worker-03
WORKER_03_IP=192.168.1.100
WORKER_03_PORT=8080
```

2. Actualizar `config_manager.py` para detectar el nuevo worker

3. Regenerar configuración:
```bash
python3 generate_config.py
```

### **Cambiar imagen Docker**
```env
DOCKER_IMAGE_NAME=mi-simulacion
DOCKER_IMAGE_TAG=v2.0
```

### **Ajustar timeouts**
```env
HTTP_TIMEOUT=15    # Conexiones lentas
TASK_TIMEOUT=120   # Tareas largas
```

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Error: Archivo .env no encontrado**
```bash
cp .env.example .env
nano .env
```

### **Error: config_manager no encontrado**
```bash
# Verificar que el archivo existe
ls -la config_manager.py

# Verificar permisos
chmod +x config_manager.py
```

### **Error: JSON no generado**
```bash
python3 generate_config.py
```

### **Workers no detectados**
1. Verificar IPs en `.env`
2. Probar conectividad: `ping IP_WORKER`
3. Verificar puertos: `telnet IP_WORKER 8080`

## 🎯 **MEJORES PRÁCTICAS**

### **1. Configuración por ambiente**
```bash
# Desarrollo
cp .env.development .env

# Producción  
cp .env.production .env
```

### **2. Backup de configuración**
```bash
# Backup automático
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

### **3. Validación de configuración**
```bash
# Antes de deploy
python3 config_manager.py
python3 generate_config.py
```

### **4. Monitoreo**
```bash
# Verificar workers regularmente
python3 orchestrator.py
# Seleccionar opción 1: Verificar workers
```

## 📚 **REFERENCIA RÁPIDA**

### **Comandos esenciales**
```bash
# Editar configuración
nano .env

# Generar JSON
python3 generate_config.py

# Verificar config
python3 config_manager.py

# Ejecutar orquestador
python3 orchestrator.py

# Ejecutar worker
./start_worker.sh
```

### **Estructura de archivos**
```
TAREA/
├── .env                      # Configuración principal
├── config_manager.py         # Gestor de configuración
├── generate_config.py        # Generador de JSON
├── config_workers.json       # Configuración JSON (auto-generado)
├── orchestrator.py          # Orquestador (usa .env)
├── worker_service.py        # Worker service (usa .env)
└── start_worker.sh          # Script de inicio
```

¡Con este sistema de configuración, el mantenimiento y despliegue del sistema es mucho más fácil y flexible! 🎉
