"""Modelo de pedido de la tienda online."""

"""Importamos uuid para no repetir id con random y datetime para guardar un registro histórico de las compras"""
import uuid
from datetime import datetime

from models.Producto import Producto
from models.Usuario import Cliente


class Pedido:
    """Registro de una compra realizada por un cliente."""

    def __init__(self, cliente: Cliente, items: list[tuple[Producto, int]]) -> None:
        """Crea un pedido a partir de un cliente y una lista de (producto, cantidad)."""
        if not isinstance(cliente, Cliente):
            raise TypeError("Un pedido solo puede estar vinculado a un Cliente.")
        if not items:
            raise ValueError("Un pedido debe contener al menos un producto.")
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.fecha: datetime = datetime.now()
        # Cada línea guarda el precio unitario del momento de la compra
        self.lineas: list[tuple[Producto, int, float]] = [
            (producto, cantidad, producto.precio) for producto, cantidad in items
        ]

    def calcular_total(self) -> float:
        """Calcula el importe total del pedido."""
        return sum(cantidad * precio for _, cantidad, precio in self.lineas)

    def __str__(self) -> str:
        """Devuelve un resumen legible del pedido."""
        detalle = "\n".join(
            f"  - {producto.nombre} x{cantidad} ({precio:.2f} €/ud) "
            f"= {cantidad * precio:.2f} €"
            for producto, cantidad, precio in self.lineas
        )
        return (
            f"Pedido [{self.id}] - {self.fecha:%d/%m/%Y %H:%M:%S}\n"
            f"Cliente: {self.cliente.nombre}\n"
            f"{detalle}\n"
            f"TOTAL: {self.calcular_total():.2f} €"
        )