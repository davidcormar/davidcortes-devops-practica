"""Esquemas Pydantic de producto: definen el JSON que entra y sale de la API."""

import math
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from models.Producto import Producto, ProductoElectronico, ProductoRopa

TipoProducto = Literal["generico", "electronico", "ropa"]

# Atributos adicionales que necesita cada tipo de producto
ATRIBUTOS_POR_TIPO: dict[str, set[str]] = {
    "generico": set(),
    "electronico": {"meses_garantia"},
    "ropa": {"talla", "color"},
}
ATRIBUTOS_ADICIONALES: set[str] = {"meses_garantia", "talla", "color"}


class ProductoCreate(BaseModel):
    """Datos que envía el cliente para crear un producto (POST /productos)."""

    tipo: TipoProducto
    nombre: str
    precio: float = Field(allow_inf_nan=False)  # rechaza NaN e Infinity (422)
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None

    @field_validator("precio", mode="before")
    @classmethod
    def precio_no_finito_como_texto(cls, valor):
        """Pasa NaN/Infinity a texto para que el error 422 se pueda devolver como JSON."""
        if isinstance(valor, float) and not math.isfinite(valor):
            return str(valor)
        return valor

    @model_validator(mode="after")
    def comprobar_atributos_del_tipo(self) -> "ProductoCreate":
        """Comprueba que vienen los atributos que exige el tipo y ninguno que no le corresponda."""
        necesarios = ATRIBUTOS_POR_TIPO[self.tipo]
        faltan = sorted(a for a in necesarios if getattr(self, a) is None)
        if faltan:
            raise ValueError(f"Un producto de tipo '{self.tipo}' necesita: {', '.join(faltan)}.")
        sobran = sorted(
            a for a in ATRIBUTOS_ADICIONALES - necesarios if getattr(self, a) is not None
        )
        if sobran:
            raise ValueError(
                f"Un producto de tipo '{self.tipo}' no admite: {', '.join(sobran)}."
            )
        return self


class ProductoRead(BaseModel):
    """Datos de un producto que la API devuelve al cliente."""

    id: str
    tipo: TipoProducto
    nombre: str
    precio: float
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None

    @classmethod
    def desde_modelo(cls, producto: Producto) -> "ProductoRead":
        """Construye la respuesta a partir de un objeto Producto (o de una subclase)."""
        datos = {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock,
        }
        # El tipo no es un atributo del modelo: se deduce de la clase del objeto
        if isinstance(producto, ProductoElectronico):
            return cls(tipo="electronico", meses_garantia=producto.meses_garantia, **datos)
        if isinstance(producto, ProductoRopa):
            return cls(tipo="ropa", talla=producto.talla, color=producto.color, **datos)
        return cls(tipo="generico", **datos)
