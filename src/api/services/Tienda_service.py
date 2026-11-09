"""Capa de servicios: gestiona de forma centralizada las operaciones de la tienda."""

from models.Pedido import Pedido
from models.Producto import Producto
from models.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Intermediario entre usuarios, productos y pedidos."""

    def __init__(self) -> None:
        """Inicializa la tienda con inventario, usuarios y pedidos vacíos."""
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    def registrar_usuario(
        self, tipo: str, nombre: str, email: str, direccion: str | None = None
    ) -> Usuario:
        """Registra un usuario de tipo 'cliente' o 'administrador' y lo devuelve."""
        if tipo == "cliente":
            if not direccion:
                raise ValueError("Un cliente necesita una dirección postal.")
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError(f"Tipo de usuario no válido: '{tipo}'.")
        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: str) -> Usuario:
        """Devuelve el usuario con ese id. Lanza KeyError si no existe."""
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise KeyError(f"No existe ningún usuario con id '{usuario_id}'.")
        return usuario

    def listar_usuarios(self) -> list[Usuario]:
        """Devuelve todos los usuarios registrados."""
        return list(self.usuarios.values())

    def anadir_producto(self, producto: Producto) -> Producto:
        """Añade al inventario un producto de cualquier categoría."""
        if producto.id in self.productos:
            raise ValueError(f"El producto '{producto.nombre}' ya está en el inventario.")
        self.productos[producto.id] = producto
        return producto

    def eliminar_producto(self, producto_id: str) -> Producto:
        """Elimina un producto del inventario por su id y lo devuelve."""
        if producto_id not in self.productos:
            raise KeyError(f"No existe ningún producto con id '{producto_id}'.")
        return self.productos.pop(producto_id)

    def obtener_producto(self, producto_id: str) -> Producto:
        """Devuelve el producto con ese id. Lanza KeyError si no existe."""
        producto = self.productos.get(producto_id)
        if producto is None:
            raise KeyError(f"No existe ningún producto con id '{producto_id}'.")
        return producto

    def listar_productos(self) -> list[Producto]:
        """Devuelve todos los productos del inventario."""
        return list(self.productos.values())

    def realizar_pedido(self, usuario_id: str, items: list[tuple[str, int]]) -> Pedido:
        """Crea un pedido si el cliente existe y hay stock de todo; descuenta el stock."""
        # 1. El usuario existe y es un cliente
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise KeyError(f"No existe ningún usuario con id '{usuario_id}'.")
        if not isinstance(usuario, Cliente):
            raise TypeError("Solo los clientes pueden realizar pedidos.")
        if not items:
            raise ValueError("El pedido debe contener al menos un producto.")

        # 2. Validar productos y agrupar cantidades (por si un producto aparece dos veces)
        cantidades: dict[str, int] = {}
        for producto_id, cantidad in items:
            if cantidad <= 0:
                raise ValueError("Las cantidades deben ser mayores que 0.")
            if producto_id not in self.productos:
                raise KeyError(f"No existe ningún producto con id '{producto_id}'.")
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

        # 3. Comprobar el stock de TODO antes de modificar NADA
        for producto_id, cantidad in cantidades.items():
            producto = self.productos[producto_id]
            if not producto.hay_stock(cantidad):
                raise ValueError(
                    f"Stock insuficiente de '{producto.nombre}': "
                    f"disponible {producto.stock}, solicitado {cantidad}."
                )

        # 4. Generar el pedido
        pedido = Pedido(
            usuario,
            [(self.productos[pid], cantidad) for pid, cantidad in cantidades.items()],
        )

        # 5. Descontar el stock y registrar el pedido
        for pid, cantidad in cantidades.items():
            self.productos[pid].actualizar_stock(cantidad, "compra")
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha, del más antiguo al más reciente."""
        if usuario_id not in self.usuarios:
            raise KeyError(f"No existe ningún usuario con id '{usuario_id}'.")
        return sorted(
            (p for p in self.pedidos if p.cliente.id == usuario_id),
            key=lambda p: p.fecha,
        )