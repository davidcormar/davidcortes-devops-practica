"""Cliente de la API REST de la tienda online, hecho con la librería requests.

Este script es totalmente independiente del servidor: no importa TiendaService ni los
modelos. Solo conoce la dirección de la API y habla con ella mediante peticiones HTTP.

Uso:
    python cliente.py
"""

import requests

# Dirección de la API. Para usar la API de otro equipo, poner aquí su IP,
# por ejemplo: BASE_URL = "http://192.168.1.34:8000"
BASE_URL = "http://localhost:8000"


def comprobar(respuesta: requests.Response, esperado: int, descripcion: str):
    """Comprueba el código de estado y devuelve el JSON de la respuesta."""
    print(f"{respuesta.request.method} {respuesta.request.path_url} -> "
          f"{respuesta.status_code}  ({descripcion})")
    if respuesta.status_code != esperado:
        raise Exception(
            f"Se esperaba {esperado} y llegó {respuesta.status_code}: {respuesta.text}"
        )
    return respuesta.json()


def main() -> None:
    """Ejecuta un flujo básico de uso de la tienda contra la API."""
    print(f"Usando la API en {BASE_URL}\n")

    print("=== 1. Crear un usuario ===")
    r = requests.post(f"{BASE_URL}/usuarios", json={
        "nombre": "Ana López",
        "email": "ana@mail.com",
        "tipo": "cliente",
        "direccion": "C/ Mayor 1, A Coruña",
    })
    ana = comprobar(r, 201, "crear usuario")
    print(f"   Creado: {ana['nombre']} (id {ana['id']})")

    print("\n=== 2. Consultar la lista de usuarios ===")
    r = requests.get(f"{BASE_URL}/usuarios")
    for usuario in comprobar(r, 200, "listar usuarios"):
        print(f"   - {usuario['nombre']} <{usuario['email']}>")

    print("\n=== 3. Crear productos ===")
    r = requests.post(f"{BASE_URL}/productos", json={
        "tipo": "electronico", "nombre": "Portátil", "precio": 899.99,
        "stock": 5, "meses_garantia": 24,
    })
    portatil = comprobar(r, 201, "crear producto electrónico")
    r = requests.post(f"{BASE_URL}/productos", json={
        "tipo": "ropa", "nombre": "Camiseta", "precio": 15.0,
        "stock": 30, "talla": "M", "color": "Azul",
    })
    camiseta = comprobar(r, 201, "crear producto de ropa")

    print("\n=== 4. Consultar la lista de productos ===")
    r = requests.get(f"{BASE_URL}/productos")
    for producto in comprobar(r, 200, "listar productos"):
        print(f"   - {producto['nombre']} ({producto['tipo']}): "
              f"{producto['precio']:.2f} €, stock {producto['stock']}")

    print("\n=== 5. Crear un pedido para Ana ===")
    r = requests.post(f"{BASE_URL}/pedidos", json={
        "cliente_id": ana["id"],
        "items": [
            {"producto_id": portatil["id"], "cantidad": 1},
            {"producto_id": camiseta["id"], "cantidad": 2},
        ],
    })
    pedido = comprobar(r, 201, "crear pedido")
    print(f"   Pedido {pedido['id']}: total {pedido['total']:.2f} €")

    print("\n=== 6. Consultar los pedidos de Ana ===")
    r = requests.get(f"{BASE_URL}/usuarios/{ana['id']}/pedidos")
    for p in comprobar(r, 200, "listar pedidos del cliente"):
        print(f"   Pedido del {p['fecha'][:19]}: {len(p['items'])} líneas, "
              f"total {p['total']:.2f} €")


if __name__ == "__main__":
    main()
