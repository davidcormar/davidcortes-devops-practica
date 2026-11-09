# Dockerfile de la API de la tienda online (src/api)

# a) Imagen base: Python 3.12 sobre Debian reducido
FROM python:3.12-slim

# No generar ficheros .pyc, mostrar los logs al momento y puerto por defecto de la API
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# b) Copiar primero solo las dependencias: si cambia el código pero no
#    requirements.txt, Docker reutiliza de la caché la capa del pip install
COPY requirements.txt .

# c) Instalar las dependencias sin guardar la caché de pip (imagen más pequeña)
RUN pip install --no-cache-dir -r requirements.txt

# d) Copiar el código fuente de la API
COPY src/api/ .

# e) Crear un usuario sin privilegios, darle permisos sobre el código y usarlo
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Documenta el puerto en el que escucha la API (se publica con -p al hacer docker run)
EXPOSE 8000

# f) Comando de inicio: 0.0.0.0 para que la API sea accesible desde fuera del contenedor
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
