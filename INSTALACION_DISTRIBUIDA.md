# 🚀 GUÍA COMPLETA: SISTEMA DISTRIBUIDO DE SIMULACIONES

Esta guía te llevará paso a paso para configurar el sistema distribuido con orquestador y workers en múltiples máquinas virtuales.

## 📋 RESUMEN DEL PROCESO

```
[PC Principal] ──(construir)──> [Imágenes TAR] ──(distribuir)──> [3 VMs]
     ↓                                                              ↓
[Orquestador]  ←──(coordina)──────────────────────────────→ [3 Workers]
```

## 🏗️ FASE 1: PREPARACIÓN EN PC PRINCIPAL

### ✅ **Paso 1.1: Verificar Prerequisites**
```cmd
# Verificar que Docker está instalado
docker --version

# Verificar que tienes todos los archivos
dir *.py
dir *.pyx
dir scripts\
dir configs\
```

### ✅ **Paso 1.2: Construir y Exportar Imágenes**
```cmd
# Ejecutar script de construcción
scripts\build_and_export.bat
```

**Lo que hace este script:**
- ✅ Construye imagen del orquestador (`particle-orchestrator.tar`)
- ✅ Construye imagen del worker (`particle-worker.tar`)
- ✅ Exporta ambas a archivos TAR
- ✅ Verifica que todo se creó correctamente

**Archivos generados:**
- `particle-orchestrator.tar` (≈500MB)
- `particle-worker.tar` (≈400MB)

### ✅ **Paso 1.3: Crear Paquetes para VMs**
```cmd
# Crear paquetes organizados para cada VM
scripts\create_vm_packages.bat
```

**Lo que hace:**
- ✅ Crea carpetas `VM_Packages\VM1_Package`, `VM2_Package`, `VM3_Package`
- ✅ Copia archivos TAR y scripts a cada paquete
- ✅ Genera instrucciones específicas para cada VM

## 🖥️ FASE 2: CONFIGURACIÓN DE MÁQUINAS VIRTUALES

### **Para cada VM (VM1, VM2, VM3):**

### ✅ **Paso 2.1: Transferir Archivos**

**Opción A - USB/Pendrive:**
1. Copiar carpeta `VM_Packages\VM1_Package` a USB
2. Conectar USB a VM1
3. Copiar carpeta a escritorio de VM1

**Opción B - Red compartida:**
```cmd
# En VM, mapear carpeta compartida de red
net use Z: \\IP_PC_PRINCIPAL\shared_folder
copy Z:\VM_Packages\VM1_Package\* C:\SimulationWorker\
```

**Opción C - SCP (si VM tiene SSH):**
```bash
scp -r VM_Packages/VM1_Package usuario@IP_VM1:~/
```

### ✅ **Paso 2.2: Instalar Docker (si no está instalado)**
```cmd
# En cada VM, ejecutar como administrador
docker-install.bat
```

**Después de la instalación:**
1. Reiniciar VM
2. Iniciar Docker Desktop
3. Aceptar términos y condiciones
4. Verificar: `docker --version`

### ✅ **Paso 2.3: Cargar Imagen Docker**
```cmd
# En cada VM, desde la carpeta copiada
load_images.bat
```

**Verifica que funcionó:**
```cmd
docker images | findstr particle-worker
```

### ✅ **Paso 2.4: Ejecutar Worker Correspondiente**

**En VM1:**
```cmd
run_worker1.bat
```

**En VM2:**
```cmd
run_worker2.bat
```

**En VM3:**
```cmd
run_worker3.bat
```

### ✅ **Paso 2.5: Verificar Workers**
```cmd
# En cada VM, verificar que el worker responde
curl http://localhost:8001/ping  # VM1
curl http://localhost:8002/ping  # VM2  
curl http://localhost:8003/ping  # VM3
```

**Respuesta esperada:**
```json
{
  "status": "online",
  "worker_id": "worker1",
  "timestamp": "2025-01-07T...",
  "current_task": null
}
```

## 🎯 FASE 3: EJECUTAR ORQUESTADOR EN PC PRINCIPAL

### ✅ **Paso 3.1: Obtener IPs de las VMs**

**En cada VM, ejecutar:**
```cmd
ipconfig | findstr IPv4
```

**Anotar las IPs:**
- VM1: `192.168.1.XXX`
- VM2: `192.168.1.YYY`  
- VM3: `192.168.1.ZZZ`

### ✅ **Paso 3.2: Ejecutar Orquestador**
```cmd
# En PC principal
scripts\run_orchestrator.bat
```

**El script te pedirá:**
- IP de VM1 (Worker 1)
- IP de VM2 (Worker 2)
- IP de VM3 (Worker 3)

### ✅ **Paso 3.3: Verificar Sistema Completo**
```cmd
# Verificar estado general
curl http://localhost:5000/status

# Hacer ping a todos los workers
curl http://localhost:5000/ping_all

# Ejecutar tareas de ejemplo
curl -X POST http://localhost:5000/execute_tasks
```

## 📊 FASE 4: MONITOREO Y USO

### ✅ **Monitoreo en Tiempo Real**
```cmd
# Cliente Python para monitoreo
python scripts\orchestrator_client.py monitor --interval 5
```

### ✅ **Comandos Útiles**

**Ver estado del sistema:**
```cmd
python scripts\orchestrator_client.py status
```

**Ver logs:**
```cmd
# Orquestador
docker logs -f particle-orchestrator

# Workers (en cada VM)
docker logs -f particle-worker-1  # VM1
docker logs -f particle-worker-2  # VM2
docker logs -f particle-worker-3  # VM3
```

**Ejecutar simulaciones personalizadas:**
```cmd
# Modificar configs\tasks.yaml y luego:
curl -X POST http://localhost:5000/execute_tasks
```

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ **Worker no responde**
```cmd
# En la VM correspondiente
docker ps -a
docker restart particle-worker-X
docker logs particle-worker-X
```

### ❌ **Orquestador no encuentra workers**
1. Verificar IPs correctas: `ping IP_VM`
2. Verificar puertos abiertos en VMs
3. Verificar firewall de Windows en VMs

### ❌ **Error de conexión**
```cmd
# En VM, abrir puertos en firewall
netsh advfirewall firewall add rule name="Particle Worker" dir=in action=allow protocol=TCP localport=8001-8003
```

### ❌ **Problemas de Docker**
```cmd
# Reiniciar Docker
net stop com.docker.service
net start com.docker.service

# O reiniciar Docker Desktop
```

## 📈 ESCALABILIDAD

### **Agregar más Workers:**
1. Crear nueva VM
2. Copiar `particle-worker.tar` 
3. Ejecutar con nuevo ID: `docker run ... --name worker4 ...`
4. Registrar en orquestador modificando `orchestrator.py`

### **Cambiar configuración de tareas:**
1. Modificar `configs\tasks.yaml`
2. Reiniciar orquestador
3. Ejecutar nuevas tareas

## 🎉 RESULTADO FINAL

Cuando todo funcione correctamente verás:

```
PC Principal (Orquestador):
├── http://localhost:5000/status
├── Distribuye tareas automáticamente
└── Recolecta resultados

VM1 (Worker 1):
├── http://IP_VM1:8001/ping
└── Ejecuta simulaciones Python/Cython

VM2 (Worker 2):  
├── http://IP_VM2:8002/ping
└── Ejecuta simulaciones Python/Cython

VM3 (Worker 3):
├── http://IP_VM3:8003/ping
└── Ejecuta simulaciones Python/Cython
```

## 📞 VERIFICACIÓN RÁPIDA

**Script de verificación completa:**
```cmd
@echo off
echo === VERIFICACION DEL SISTEMA DISTRIBUIDO ===
echo.
echo 1. Verificando orquestador...
curl -s http://localhost:5000/status
echo.
echo 2. Verificando workers...
curl -s http://localhost:5000/ping_all
echo.
echo 3. Sistema listo para ejecutar tareas!
pause
```

¡Con esta guía tendrás tu sistema distribuido funcionando perfectamente! 🚀
