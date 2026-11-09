"""Productos de la tienda online."""


"""Importamos uuid para poder generar un id completamente aleatorio ya que con random se pueden repetir"""
import uuid


class Producto:
    """Producto genérico de la tienda. Clase base del resto de productos."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto con un identificador único generado automáticamente."""
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if stock < 0:
            raise ValueError("El stock inicial no puede ser negativo.")
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si hay unidades suficientes para servir la cantidad solicitada."""
        return 0 < cantidad <= self.stock

    def actualizar_stock(self, cantidad: int, tipo: str) -> None:
        """Actualiza el stock según el tipo de operación: 'compra' o 'reposicion'."""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")
        if tipo == "reposicion":
            self.stock += cantidad
        elif tipo == "compra":
            if not self.hay_stock(cantidad):
                raise ValueError(
                    f"Stock insuficiente de '{self.nombre}': "
                    f"disponible {self.stock}, solicitado {cantidad}."
                )
            self.stock -= cantidad
        else:
            raise ValueError(f"Tipo de operación no válido: '{tipo}'.")

    def __str__(self) -> str:
        """Devuelve las características principales del producto."""
        return (
            f"[{self.id}] {self.nombre} - {self.precio:.2f} € "
            f"(stock: {self.stock})"
        )


class ProductoElectronico(Producto):
    """Producto electrónico con garantía."""

    def __init__(
        self, nombre: str, precio: float, stock: int, meses_garantia: int
    ) -> None:
        """Crea un producto electrónico con sus meses de garantía."""
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        """Añade la garantía a la descripción base."""
        return f"{super().__str__()} | Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    """Prenda de ropa con talla y color."""

    def __init__(
        self, nombre: str, precio: float, stock: int, talla: str, color: str
    ) -> None:
        """Crea una prenda con su talla y color."""
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        """Añade talla y color a la descripción base."""
        return f"{super().__str__()} | Talla: {self.talla} | Color: {self.color}"