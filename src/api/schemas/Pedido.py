"""Esquemas Pydantic de pedido: definen el JSON que entra y sale de la API."""

from datetime import datetime

from pydantic import BaseModel

from models.Pedido import Pedido


class PedidoItemCreate(BaseModel):
    """Una línea del pedido que envía el cliente: qué producto y cuántas unidades."""

    producto_id: str
    cantidad: int


class PedidoCreate(BaseModel):
    """Datos que envía el cliente para crear un pedido (POST /pedidos)."""

    cliente_id: str
    items: list[PedidoItemCreate]


class PedidoItemRead(BaseModel):
    """Una línea del pedido tal y como la devuelve la API."""

    producto_id: str
    cantidad: int
    precio_unitario: float


class PedidoRead(BaseModel):
    """Pedido completo que devuelve la API: fecha, cliente, total y líneas."""

    id: str
    fecha: datetime
    cliente_id: str
    total: float
    items: list[PedidoItemRead]

    @classmethod
    def desde_modelo(cls, pedido: Pedido) -> "PedidoRead":
        """Construye la respuesta a partir de un objeto Pedido del dominio."""
        return cls(
            id=pedido.id,
            fecha=pedido.fecha,
            cliente_id=pedido.cliente.id,
            total=round(pedido.calcular_total(), 2),
            items=[
                PedidoItemRead(
                    producto_id=producto.id, cantidad=cantidad, precio_unitario=precio
                )
                for producto, cantidad, precio in pedido.lineas
            ],
        )
