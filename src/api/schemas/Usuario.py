"""Esquemas Pydantic de usuario: definen el JSON que entra y sale de la API."""

from pydantic import BaseModel

from models.Usuario import Usuario


class UsuarioCreate(BaseModel):
    """Datos que envía el cliente para registrar un usuario (POST /usuarios)."""

    nombre: str
    email: str
    tipo: str
    direccion: str | None = None


class UsuarioRead(BaseModel):
    """Datos de un usuario que la API devuelve al cliente."""

    id: str
    nombre: str
    email: str
    es_admin: bool

    @classmethod
    def desde_modelo(cls, usuario: Usuario) -> "UsuarioRead":
        """Construye la respuesta a partir de un objeto Usuario del dominio."""
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin(),
        )
