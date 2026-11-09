"""Modelos de usuarios de la tienda online."""

"""Volvemos a importar uuid en vez de random para que no se puedan repetir los id"""
import uuid


class Usuario:
    """Persona que interactúa con la tienda. Clase base de los tipos de usuario."""

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario con un identificador único generado automáticamente."""
        if "@" not in email:
            raise ValueError(f"Email no válido: '{email}'.")
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Indica si el usuario es administrador. Por defecto, no lo es."""
        return False

    def __str__(self) -> str:
        """Devuelve los datos principales del usuario."""
        return f"[{self.id}] {self.nombre} <{self.email}>"


class Cliente(Usuario):
    """Usuario que realiza compras en la tienda."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """Crea un cliente con su dirección postal."""
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        """Añade la dirección a la descripción base."""
        return f"{super().__str__()} | Dirección: {self.direccion}"


class Administrador(Usuario):
    """Usuario gestor de la tienda. No tiene def __init__ ya que como no añade atributos nuevos hereda los del padre."""

    def is_admin(self) -> bool:
        """Los administradores siempre devuelven True."""
        return True

    def __str__(self) -> str:
        """Marca al usuario como administrador en su descripción."""
        return f"{super().__str__()} | Rol: Administrador"