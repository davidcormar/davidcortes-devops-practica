# Tienda online - DevOps práctica

**Autor:** David Cortés Martínez

Asignatura: Arquitectura del Software (UIE).

## Descripción

Aplicación Python de una **tienda online** expuesta como **API REST** con FastAPI.
Permite gestionar usuarios (clientes y administradores), productos (genéricos,
electrónicos y de ropa) y pedidos. Los datos se guardan en memoria.

El proyecto parte del código de la Práctica 2, se versiona con Git/GitHub y se
contenedoriza con Docker.

## Estructura del repositorio

```
.
├── Dockerfile            # Imagen de la API
├── .dockerignore         # Ficheros que no se envían a Docker al construir
├── docker-compose.yml    # (Extra) Levanta la API y el frontend juntos
├── requirements.txt      # Dependencias de la API con versiones fijadas
└── src/
    ├── api/              # API REST (FastAPI + Pydantic): main.py, models, schemas, services
    ├── cliente/          # Cliente Python que consume la API con requests
    └── frontend/         # Página web que consume la API con fetch (+ Dockerfile con nginx)
```

## Docker

Requisito: tener Docker instalado y arrancado (en Windows, Docker Desktop).
Todos los comandos se ejecutan desde la **raíz del repositorio**.

### 1. Construir la imagen

```bash
docker build -t tienda-online:1.0 .
```

- `-t tienda-online:1.0`: nombre y etiqueta (versión) de la imagen.
- `.`: el contexto de construcción es la carpeta actual (usa el `Dockerfile` y el `.dockerignore` de la raíz).

Comprobar que se ha creado:

```bash
docker image ls tienda-online
```

### 2. Ejecutar el contenedor

```bash
docker run --name tienda -p 8000:8000 tienda-online:1.0
```

- `-p 8000:8000`: publica el puerto 8000 del contenedor en el 8000 del equipo (`HOST:CONTENEDOR`).
- `--name tienda`: nombre del contenedor para gestionarlo después.

Otros ejemplos:

```bash
# En segundo plano (-d) y borrando el contenedor al pararlo (--rm)
docker run -d --rm --name tienda -p 8000:8000 tienda-online:1.0

# Publicar la API en otro puerto del equipo (http://localhost:8081)
docker run --rm -p 8081:8000 tienda-online:1.0

# Cambiar el puerto interno con la variable de entorno PORT
docker run --rm -e PORT=9000 -p 9000:9000 tienda-online:1.0
```

Gestión del contenedor:

```bash
docker ps              # contenedores en ejecución
docker logs tienda     # salida de la API
docker stop tienda     # parar
docker start tienda    # volver a arrancar el mismo contenedor
docker rm tienda       # borrarlo (una vez parado)
```

> Los datos (usuarios, productos, pedidos) se guardan **en memoria**: al reiniciar
> o recrear el contenedor la tienda vuelve a estar vacía.

### 3. Variables de entorno soportadas

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `PORT`   | `8000`            | Puerto en el que escucha la API dentro del contenedor. Si se cambia, hay que publicar ese mismo puerto con `-p`. |

La aplicación no usa claves ni secretos.

### 4. Salida esperada y pruebas

Al arrancar, `docker logs tienda` (o la terminal) debe mostrar:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Pasos de prueba:

1. Abrir **http://localhost:8000/docs** (Swagger). Desde ahí se pueden probar todos los endpoints con *Try it out*.
2. Endpoints disponibles:

   | Método | Ruta | Descripción | Respuesta correcta |
   |--------|------|-------------|--------------------|
   | POST   | `/usuarios` | Crear usuario (cliente o administrador) | 201 |
   | GET    | `/usuarios` | Listar usuarios | 200 |
   | GET    | `/usuarios/{usuario_id}` | Obtener un usuario | 200 / 404 |
   | POST   | `/productos` | Crear producto (generico, electronico o ropa) | 201 |
   | GET    | `/productos` | Listar productos | 200 |
   | GET    | `/productos/{producto_id}` | Obtener un producto | 200 / 404 |
   | DELETE | `/productos/{producto_id}` | Eliminar un producto | 200 / 404 |
   | POST   | `/pedidos` | Crear pedido (descuenta stock) | 201 |
   | GET    | `/usuarios/{cliente_id}/pedidos` | Pedidos de un cliente | 200 / 404 |

   Errores: 400 (regla de negocio, p. ej. stock insuficiente), 404 (no existe), 422 (JSON con datos no válidos).

3. Prueba rápida con `curl` (Git Bash, Linux o macOS):

   ```bash
   curl http://localhost:8000/productos
   # -> []

   curl -X POST http://localhost:8000/usuarios \
        -H "Content-Type: application/json" \
        -d '{"nombre": "Ana", "email": "ana@mail.com", "tipo": "cliente", "direccion": "C/ Mayor 1"}'
   # -> 201 {"id": "...", "nombre": "Ana", "email": "ana@mail.com", "es_admin": false}
   ```

4. Prueba completa con el cliente Python (con el contenedor en marcha):

   ```bash
   pip install -r src/cliente/requirements.txt
   python src/cliente/cliente.py
   ```

   Debe imprimir cada petición con su código: `POST /usuarios -> 201`, `GET /usuarios -> 200`,
   `POST /productos -> 201` (x2), `GET /productos -> 200`, `POST /pedidos -> 201` y
   `GET /usuarios/{id}/pedidos -> 200`.

5. Frontend: abrir `src/frontend/index.html` con doble clic en el navegador (usa la API de `http://localhost:8000`).

### 5. Publicar la imagen en Docker Hub

```bash
docker tag tienda-online:1.0 davidcormar17/tienda-online:1.0
docker login
docker push davidcormar17/tienda-online:1.0
```

### 6. Descargar (pull) y ejecutar la imagen publicada

En cualquier equipo con Docker, sin necesidad de clonar el repositorio:

```bash
docker pull davidcormar17/tienda-online:1.0
docker run --rm -p 8000:8000 davidcormar17/tienda-online:1.0
```

Imagen en Docker Hub: https://hub.docker.com/r/davidcormar17/tienda-online

### 7. (Extra) API + frontend con Docker Compose

`docker-compose.yml` levanta dos contenedores en la misma red:

- `api`: la imagen de la API (`Dockerfile` de la raíz), en http://localhost:8000.
- `frontend`: nginx sirviendo la web (`src/frontend/Dockerfile`), en **http://localhost:8080**.
  nginx reenvía las peticiones `/api/...` al contenedor `api` (`http://api:8000`),
  así que los dos contenedores se comunican por la red de Docker.

```bash
docker compose up --build     # construir y arrancar ambos (Ctrl+C para parar)
docker compose up -d --build  # en segundo plano
docker compose down           # parar y borrar los contenedores
```

## Ejecución sin Docker (local)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
cd src/api
uvicorn main:app --reload
```
