"""Punto de entrada de la aplicación: expone la tienda online como una API REST con FastAPI.

Este módulo es la capa de exposición del servicio: recibe las peticiones HTTP, valida los
datos con los esquemas Pydantic, llama a TiendaService y traduce el resultado (o los errores
del servicio) a respuestas HTTP con el código de estado adecuado.

Ejecución (desde esta carpeta):
    uvicorn main:app --reload                    # solo accesible desde este equipo
    uvicorn main:app --reload --host 0.0.0.0     # accesible desde otros equipos de la red
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models.Producto import Producto, ProductoElectronico, ProductoRopa
from schemas.Pedido import PedidoCreate, PedidoRead
from schemas.Producto import ProductoCreate, ProductoRead
from schemas.Usuario import UsuarioCreate, UsuarioRead
from services.Tienda_service import TiendaService

app = FastAPI(title="Tienda online")

# Permite que el frontend (una página web servida desde otro origen) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Una única instancia del servicio: todas las peticiones trabajan sobre los mismos datos
tienda = TiendaService()


def no_encontrado(error: KeyError) -> HTTPException:
    """Traduce un KeyError del servicio («no existe») a un error HTTP 404."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.args[0])


def peticion_incorrecta(error: Exception) -> HTTPException:
    """Traduce un error de regla de negocio del servicio a un error HTTP 400."""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


# ---------------------------------------------------------------- Usuarios


@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    """Registra un nuevo usuario (cliente o administrador)."""
    try:
        usuario = tienda.registrar_usuario(
            datos.tipo, datos.nombre, datos.email, datos.direccion
        )
    except ValueError as error:
        raise peticion_incorrecta(error)
    return UsuarioRead.desde_modelo(usuario)


@app.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios() -> list[UsuarioRead]:
    """Devuelve la lista de usuarios registrados."""
    return [UsuarioRead.desde_modelo(u) for u in tienda.listar_usuarios()]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    """Devuelve un usuario concreto a partir de su id."""
    try:
        usuario = tienda.obtener_usuario(usuario_id)
    except KeyError as error:
        raise no_encontrado(error)
    return UsuarioRead.desde_modelo(usuario)


# ---------------------------------------------------------------- Productos


@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    """Crea un producto genérico, electrónico o de ropa y lo añade al inventario."""
    try:
        if datos.tipo == "electronico":
            producto = ProductoElectronico(
                datos.nombre, datos.precio, datos.stock, datos.meses_garantia
            )
        elif datos.tipo == "ropa":
            producto = ProductoRopa(
                datos.nombre, datos.precio, datos.stock, datos.talla, datos.color
            )
        else:
            producto = Producto(datos.nombre, datos.precio, datos.stock)
        tienda.anadir_producto(producto)
    except ValueError as error:
        raise peticion_incorrecta(error)
    return ProductoRead.desde_modelo(producto)


@app.get("/productos", response_model=list[ProductoRead])
def listar_productos() -> list[ProductoRead]:
    """Devuelve todos los productos del inventario."""
    return [ProductoRead.desde_modelo(p) for p in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: str) -> ProductoRead:
    """Devuelve un producto concreto a partir de su id."""
    try:
        producto = tienda.obtener_producto(producto_id)
    except KeyError as error:
        raise no_encontrado(error)
    return ProductoRead.desde_modelo(producto)


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: str) -> dict[str, str]:
    """Elimina un producto del inventario."""
    try:
        tienda.eliminar_producto(producto_id)
    except KeyError as error:
        raise no_encontrado(error)
    return {"mensaje": "Producto eliminado correctamente"}


# ---------------------------------------------------------------- Pedidos


@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    """Crea un pedido comprobando que existen el cliente y los productos y que hay stock."""
    items = [(item.producto_id, item.cantidad) for item in datos.items]
    try:
        pedido = tienda.realizar_pedido(datos.cliente_id, items)
    except KeyError as error:
        raise no_encontrado(error)
    except (ValueError, TypeError) as error:
        raise peticion_incorrecta(error)
    return PedidoRead.desde_modelo(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead])
def listar_pedidos_cliente(cliente_id: str) -> list[PedidoRead]:
    """Devuelve los pedidos de un cliente, del más antiguo al más reciente."""
    try:
        pedidos = tienda.listar_pedidos_usuario(cliente_id)
    except KeyError as error:
        raise no_encontrado(error)
    return [PedidoRead.desde_modelo(p) for p in pedidos]
