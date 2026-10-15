"""
Pruebas automáticas de la API.

Ejecuta con:  pytest -v

TestClient simula peticiones HTTP sin necesidad de levantar el servidor.
Cada función que empieza con "test_" es una prueba que pytest ejecuta.
"assert" verifica que algo sea verdadero; si no lo es, la prueba falla.
"""

from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)


def test_health_check():
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_listar_productos_con_limite():
    respuesta = cliente.get("/productos", params={"limite": 5})
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 5


def test_producto_inexistente_da_404():
    respuesta = cliente.get("/productos/99999")
    assert respuesta.status_code == 404


def test_crear_producto():
    nuevo = {"nombre": "Termo Eco", "categoria": "Hogar", "precio": 299.5, "stock": 8}
    respuesta = cliente.post("/productos", json=nuevo)
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Termo Eco"
    assert "id" in respuesta.json()


def test_crear_producto_invalido_da_422():
    # Precio negativo: Pydantic lo rechaza automáticamente.
    respuesta = cliente.post(
        "/productos", json={"nombre": "X1", "categoria": "Hogar", "precio": -5, "stock": 1}
    )
    assert respuesta.status_code == 422


def test_crear_cliente_y_rechazar_duplicado():
    datos = {"nombre": "Prueba Pytest", "email": "prueba@ejemplo.com", "ciudad": "León"}
    assert cliente.post("/clientes", json=datos).status_code == 201
    assert cliente.post("/clientes", json=datos).status_code == 409
