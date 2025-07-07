# 🎯 RESUMEN EJECUTIVO: QUÉ HACER Y DÓNDE

## 🖥️ EN TU COMPUTADOR ACTUAL (PC Principal)

### ⚡ **OPCIÓN RÁPIDA - Todo en tu PC:**
```cmd
# Ejecutar script maestro y seleccionar opción 1
SETUP_MAESTRO.bat
```

### 🌐 **OPCIÓN DISTRIBUIDA - Múltiples VMs:**

#### **Paso 1: Preparar TODO**
```cmd
# Ejecutar script maestro y seleccionar opción 2
SETUP_MAESTRO.bat
```

#### **Paso 2: Crear VMs y distribuir**
1. Crear 3 máquinas virtuales (VM1, VM2, VM3)
2. Instalar Windows en cada una
3. Copiar paquetes:
   - `VM_Packages\VM1_Package\` → VM1
   - `VM_Packages\VM2_Package\` → VM2  
   - `VM_Packages\VM3_Package\` → VM3

#### **Paso 3: Ejecutar Orquestador**
```cmd
# En tu PC, ejecutar script maestro y seleccionar opción 3
SETUP_MAESTRO.bat
```

---

## 💻 EN CADA MÁQUINA VIRTUAL

### **VM1 (Worker 1):**
```cmd
# Después de copiar VM1_Package:
cd VM1_Package

# 1. Instalar Docker (si no está)
docker-install.bat

# 2. Cargar imagen
load_images.bat

# 3. Ejecutar worker
run_worker1.bat
```

### **VM2 (Worker 2):**
```cmd
# Después de copiar VM2_Package:
cd VM2_Package

# 1. Instalar Docker (si no está)
docker-install.bat

# 2. Cargar imagen  
load_images.bat

# 3. Ejecutar worker
run_worker2.bat
```

### **VM3 (Worker 3):**
```cmd
# Después de copiar VM3_Package:
cd VM3_Package

# 1. Instalar Docker (si no está)
docker-install.bat

# 2. Cargar imagen
load_images.bat

# 3. Ejecutar worker
run_worker3.bat
```

---

## 🚀 VERIFICACIÓN FINAL

### **En tu PC Principal:**
```cmd
# Verificar que todo funciona
scripts\verify_system.bat

# Ejecutar simulaciones
curl -X POST http://localhost:5000/execute_tasks

# Monitorear en tiempo real
python scripts\orchestrator_client.py monitor
```

---

## 📋 ORDEN DE EJECUCIÓN

| Orden | Máquina | Acción |
|-------|---------|--------|
| 1 | **PC Principal** | `SETUP_MAESTRO.bat` → Opción 2 |
| 2 | **VM1** | `docker-install.bat` → `load_images.bat` → `run_worker1.bat` |
| 3 | **VM2** | `docker-install.bat` → `load_images.bat` → `run_worker2.bat` |
| 4 | **VM3** | `docker-install.bat` → `load_images.bat` → `run_worker3.bat` |
| 5 | **PC Principal** | `SETUP_MAESTRO.bat` → Opción 3 |
| 6 | **PC Principal** | `scripts\verify_system.bat` |

---

## 🎉 RESULTADO FINAL

```
PC Principal:     http://localhost:5000        (Orquestador)
VM1:             http://IP_VM1:8001           (Worker 1)
VM2:             http://IP_VM2:8002           (Worker 2)  
VM3:             http://IP_VM3:8003           (Worker 3)
```

**¡El orquestador distribuirá automáticamente las simulaciones entre las 3 VMs!**

---

## ⚡ TL;DR (Muy Rápido)

**Si solo quieres probar:**
```cmd
SETUP_MAESTRO.bat → Opción 1
```

**Si quieres ambiente real distribuido:**
```cmd
PC: SETUP_MAESTRO.bat → Opción 2
Cada VM: docker-install.bat → load_images.bat → run_workerX.bat  
PC: SETUP_MAESTRO.bat → Opción 3
```

**¡Ya está! 🚀**
