# Paquete de distribución para Máquinas Virtuales

Este paquete contiene todos los archivos necesarios para ejecutar un worker de simulación de partículas en una máquina virtual.

## Contenido del Paquete

```
VM_Package/
├── particle-worker.tar         # Imagen Docker del worker
├── load_images.bat            # Script para cargar imagen Docker
├── run_worker1.bat            # Script para ejecutar Worker 1 (VM1)
├── run_worker2.bat            # Script para ejecutar Worker 2 (VM2)
├── run_worker3.bat            # Script para ejecutar Worker 3 (VM3)
├── docker-install.bat         # Script para instalar Docker (opcional)
└── VM_SETUP.md               # Estas instrucciones
```

## Requisitos Previos

### En cada Máquina Virtual:

1. **Sistema Operativo**: Windows 10/11 o Linux
2. **Docker Desktop** instalado y funcionando
3. **Al menos 2GB de RAM** disponible
4. **Al menos 1GB de espacio en disco** disponible

## Instalación Paso a Paso

### PASO 1: Preparar la Máquina Virtual

#### Si no tienes Docker instalado:
```cmd
# Ejecutar como administrador
docker-install.bat
```

#### Si ya tienes Docker:
```cmd
# Verificar que Docker funciona
docker --version
docker run hello-world
```

### PASO 2: Cargar la Imagen Docker

```cmd
# Ejecutar en la VM
load_images.bat
```

Este script:
- Verifica que existe `particle-worker.tar`
- Carga la imagen en Docker
- Verifica que se cargó correctamente

### PASO 3: Ejecutar el Worker

**Para VM1 (Worker 1):**
```cmd
run_worker1.bat
```

**Para VM2 (Worker 2):**
```cmd
run_worker2.bat
```

**Para VM3 (Worker 3):**
```cmd
run_worker3.bat
```

## Verificación

### Comprobar que el Worker funciona:

```cmd
# Verificar contenedor ejecutándose
docker ps

# Hacer ping al worker
curl http://localhost:8001/ping   # Para Worker 1
curl http://localhost:8002/ping   # Para Worker 2
curl http://localhost:8003/ping   # Para Worker 3
```

### Respuesta esperada:
```json
{
  "status": "online",
  "worker_id": "worker1",
  "timestamp": "2025-01-07T10:30:00",
  "current_task": null
}
```

## Comandos Útiles

### Ver logs del worker:
```cmd
docker logs -f particle-worker-1   # Worker 1
docker logs -f particle-worker-2   # Worker 2
docker logs -f particle-worker-3   # Worker 3
```

### Reiniciar worker:
```cmd
docker restart particle-worker-1
```

### Detener worker:
```cmd
docker stop particle-worker-1
```

### Ver estado del contenedor:
```cmd
docker ps -a
```

## Solución de Problemas

### Worker no inicia:
1. Verificar que Docker está ejecutándose: `docker ps`
2. Verificar imagen cargada: `docker images | findstr particle-worker`
3. Ver logs: `docker logs particle-worker-1`

### Worker no responde a ping:
1. Verificar puerto abierto: `netstat -an | findstr 8001`
2. Verificar firewall de Windows
3. Reiniciar contenedor: `docker restart particle-worker-1`

### Error de memoria:
1. Cerrar aplicaciones innecesarias
2. Reiniciar VM
3. Verificar recursos: `docker stats`

## Información de Red

### Puertos utilizados:
- **Worker 1**: Puerto 8001
- **Worker 2**: Puerto 8002  
- **Worker 3**: Puerto 8003

### Configuración de Firewall:
Si tienes problemas de conexión, asegúrate de que estos puertos estén abiertos:

```cmd
# Windows Firewall
netsh advfirewall firewall add rule name="Particle Worker" dir=in action=allow protocol=TCP localport=8001-8003
```

## Notas Importantes

1. **Un worker por VM**: Cada máquina virtual debe ejecutar SOLO el worker que le corresponde
2. **Persistencia**: Los workers se reinician automáticamente si se reinicia la VM
3. **Logs**: Los logs se guardan en la carpeta `logs/` de la VM
4. **Resultados**: Los resultados se guardan en la carpeta `results/` de la VM

## Contacto

Si tienes problemas con la instalación o ejecución, revisa:
1. Los logs de Docker: `docker logs particle-worker-X`
2. El estado del sistema: `docker ps -a`
3. Los recursos disponibles: `docker stats`
