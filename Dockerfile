FROM python:3.9-slim

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Compilar Cython si es necesario (setup.py existe)
RUN python setup.py build_ext --inplace || echo "No setup.py found, skipping Cython compilation"

# Punto de entrada por defecto
CMD ["python", "benchmark.py"]
