# Dockerfile para las máquinas de simulación
FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para compilar Cython
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Compilar extensión Cython
RUN python setup.py build_ext --inplace

# Exponer puerto para comunicación
EXPOSE 8000

# Comando por defecto
CMD ["python", "-m", "http.server", "8000"]
