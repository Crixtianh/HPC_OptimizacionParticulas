# 🐳 ETAPA 2: DOCKERIZACIÓN - README

## 📋 **RESUMEN DE LA ETAPA**

Esta etapa transforma el proyecto de simulación de partículas en un sistema **dockerizado** y **empaquetable** para distribución en máquinas virtuales usando **Docker + TAR**.

---

## 🎯 **OBJETIVOS COMPLETADOS**

✅ **Containerización** de los benchmarks Python y Cython  
✅ **Gestión de dependencias** automatizada  
✅ **Scripts de build** multiplataforma (Linux/Windows)  
✅ **Sistema de empaquetado TAR** para distribución  
✅ **Testing automatizado** de containers  
✅ **Preparación** para despliegue en VMs  

---

## 📁 **ARCHIVOS CREADOS**

### **🐳 Docker Configuration**

#### `Dockerfile`
- **Propósito**: Define la imagen Docker para los benchmarks
- **Base**: `python:3.9-slim` (imagen ligera con Python)
- **Dependencias**: Instala `gcc`, `g++` para compilación de Cython
- **Funcionalidad**: 
  - Instala dependencias desde `requirements.txt`
  - Copia todo el código fuente
  - Compila extensiones Cython automáticamente
  - Configura punto de entrada por defecto

#### `requirements.txt`
- **Propósito**: Define dependencias Python exactas
- **Contenido**:
  - `numpy==1.24.3` - Para operaciones matemáticas
  - `cython==0.29.36` - Para compilación de extensiones optimizadas

#### `.dockerignore`
- **Propósito**: Excluye archivos innecesarios del contexto Docker
- **Optimización**: Reduce tamaño de imagen y tiempo de build
- **Excluye**: `__pycache__`, `.git`, archivos temporales, logs

---

### **🔧 Scripts de Automatización**

#### `build_docker.sh` / `build_docker.bat`
- **Propósito**: Construye y prueba la imagen Docker
- **Funcionalidad**:
  - Ejecuta `docker build` con tag `particle-simulation:latest`
  - Verifica construcción exitosa
  - Ejecuta pruebas básicas automáticamente
  - Muestra información de la imagen creada
- **Multiplataforma**: Versión bash (Linux/macOS) y batch (Windows)

#### `test_docker.sh` / `test_docker.bat`
- **Propósito**: Testing exhaustivo de containers
- **Pruebas realizadas**:
  1. `benchmark.py` con valores por defecto
  2. `benchmark.py` con parámetros personalizados (100 500 42)
  3. `benchmark_cython.py` con valores por defecto  
  4. `benchmark_cython.py` con parámetros personalizados
  5. Verificación de archivos en container
- **Validación**: Confirma que ambos benchmarks funcionan correctamente

#### `package_project.sh`
- **Propósito**: Empaqueta el proyecto completo en archivo TAR
- **Funcionalidad**:
  - Crea archivo `particle-simulation-YYYYMMDD-HHMMSS.tar.gz`
  - Excluye archivos innecesarios (`__pycache__`, `.git`, etc.)
  - Incluye todo el código fuente y configuración Docker
  - Muestra contenido y tamaño del archivo
  - Proporciona instrucciones de transferencia a VMs

---

## 🚀 **CÓMO USAR**

### **1. Construir Imagen Docker**

**En Windows:**
```cmd
build_docker.bat
```

**En Linux/macOS:**
```bash
chmod +x build_docker.sh
./build_docker.sh
```

### **2. Probar Containers**

**En Windows:**
```cmd
test_docker.bat
```

**En Linux/macOS:**
```bash
chmod +x test_docker.sh
./test_docker.sh
```

### **3. Empaquetar para Distribución**

**En Linux/macOS:**
```bash
chmod +x package_project.sh
./package_project.sh
```

### **4. Ejecutar Simulaciones Manualmente**

```bash
# Con valores por defecto
docker run --rm particle-simulation:latest python benchmark.py

# Con parámetros personalizados
docker run --rm particle-simulation:latest python benchmark.py 200 1000 123

# Benchmark optimizado con Cython
docker run --rm particle-simulation:latest python benchmark_cython.py 500 2000 456
```

---

## 🔄 **FLUJO DE DISTRIBUCIÓN A VMs**

```mermaid
graph LR
A[Desarrollo Local] --> B[Docker Build]
B --> C[Testing Local]
C --> D[Empaquetado TAR]
D --> E[Transferencia a VMs]
E --> F[Extracción en VMs]
F --> G[Docker Build en VMs]
G --> H[Ejecución Distribuida]
```

### **Pasos para VMs:**

1. **Empaquetar proyecto:**
   ```bash
   ./package_project.sh
   ```

2. **Transferir a VM:**
   ```bash
   scp particle-simulation-*.tar.gz usuario@ip-vm:/home/worker/
   ```

3. **En la VM:**
   ```bash
   tar -xzf particle-simulation-*.tar.gz
   cd TAREA/
   docker build -t particle-simulation:latest .
   ```

4. **Ejecutar en VM:**
   ```bash
   docker run particle-simulation:latest python benchmark.py 100 1000 42
   ```

---

## ✨ **VENTAJAS DE LA DOCKERIZACIÓN**

### **🔒 Aislamiento**
- Cada simulación corre en entorno aislado
- No hay conflictos entre dependencias
- Comportamiento predecible en todas las VMs

### **📦 Portabilidad**
- Misma imagen funciona en cualquier VM con Docker
- No importa la distribución Linux de la VM
- Dependencias incluidas en la imagen

### **⚡ Escalabilidad**
- Fácil replicación en múltiples VMs
- Containers livianos para paralelización
- Gestión de recursos automática

### **🔧 Mantenibilidad**
- Updates centralizados vía nuevas imágenes
- Versionado de releases
- Rollback sencillo si hay problemas

---

## 🔮 **PREPARACIÓN PARA ETAPA 3**

Esta dockerización prepara el terreno para:

- **Despliegue en VMs** con Ubuntu/Debian
- **Comunicación worker-orquestador** via HTTP
- **Distribución automática** de código
- **Ejecución distribuida** de simulaciones

### **Requisitos para VMs:**
- Ubuntu 20.04+ o Debian 11+
- Docker Engine instalado
- Conectividad de red con el orquestador
- SSH habilitado para transferencias

---

## 📊 **VERIFICACIÓN DE ÉXITO**

Para confirmar que esta etapa funciona correctamente:

1. ✅ `docker images` muestra `particle-simulation:latest`
2. ✅ Ambos benchmarks ejecutan sin errores
3. ✅ Parámetros CLI funcionan correctamente
4. ✅ Se puede crear archivo TAR
5. ✅ Container es reproducible entre ejecuciones

---

## 🚀 **PRÓXIMOS PASOS (ETAPA 3)**

1. **Instalar VirtualBox** y crear 3 VMs Ubuntu
2. **Configurar red** entre host y VMs
3. **Instalar Docker** en cada VM
4. **Transferir y probar** este proyecto dockerizado
5. **Preparar** sistema de comunicación worker

---

**🎉 ETAPA 2 COMPLETADA EXITOSAMENTE 🎉**
