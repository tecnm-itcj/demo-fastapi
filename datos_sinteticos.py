"""
=====================================================================
 GENERADOR DE DATOS SINTÉTICOS
=====================================================================
"Datos sintéticos" son datos inventados por un programa, pero que se
ven realistas. Son muy útiles para:
  * Hacer demos y prototipos sin exponer información real.
  * Probar una API antes de tener una base de datos de verdad.

Aquí los generamos solo con la librería estándar de Python (el módulo
"random"), así no necesitamos instalar nada extra.
=====================================================================
"""

import random
from datetime import date, timedelta

# Fijamos una "semilla" (seed). Esto hace que los números aleatorios
# sean SIEMPRE los mismos cada vez que arranca el programa.
# Así todos los alumnos ven exactamente los mismos datos y pueden
# comparar resultados. Si cambias el número, cambian los datos.
random.seed(42)

# ---------------------------------------------------------------------
# Catálogos de valores base. El generador combina estos valores al azar.
# ---------------------------------------------------------------------

# Diccionario: cada categoría tiene su lista de productos posibles.
PRODUCTOS_POR_CATEGORIA = {
    "Electrónica": ["Audífonos", "Teclado", "Mouse", "Monitor", "Bocina", "Cargador"],
    "Hogar": ["Lámpara", "Cafetera", "Licuadora", "Tostador", "Ventilador"],
    "Deportes": ["Balón", "Tapete de yoga", "Mancuernas", "Raqueta", "Bicicleta"],
    "Papelería": ["Cuaderno", "Plumas", "Mochila", "Calculadora", "Marcatextos"],
}

# Adjetivos para que los nombres de producto se vean más variados.
ADJETIVOS = ["Pro", "Básico", "Deluxe", "Compacto", "Eco", "Plus", "Mini"]

NOMBRES = ["Ana", "Luis", "María", "Carlos", "Sofía", "Jorge", "Valeria",
           "Diego", "Fernanda", "Miguel", "Daniela", "Ricardo"]
APELLIDOS = ["García", "Hernández", "López", "Martínez", "González",
             "Pérez", "Rodríguez", "Sánchez", "Ramírez", "Torres"]
CIUDADES = ["Ciudad de México", "Guadalajara", "Monterrey", "Puebla",
            "Querétaro", "Mérida", "Tijuana", "León"]


def _fecha_aleatoria(dias_atras: int = 365) -> str:
    """Devuelve una fecha al azar dentro de los últimos "dias_atras" días.

    El guion bajo al inicio del nombre (_fecha_aleatoria) es una
    convención en Python para decir: "esta función es de uso interno".
    """
    fecha = date.today() - timedelta(days=random.randint(0, dias_atras))
    # isoformat() la convierte a texto con formato AAAA-MM-DD.
    return fecha.isoformat()


def _quitar_acentos(texto: str) -> str:
    """Quita acentos para poder usar el texto dentro de un correo."""
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.translate(reemplazos)


def generar_productos(cantidad: int = 20) -> list[dict]:
    """Crea una lista de productos inventados.

    Cada producto es un diccionario con las mismas llaves que el modelo
    "Producto" definido en main.py (id, nombre, categoria, precio, stock,
    fecha_alta). Si no coinciden, FastAPI marcaría error al responder.
    """
    productos = []
    # range(1, cantidad + 1) produce 1, 2, 3, ..., cantidad.
    for i in range(1, cantidad + 1):
        categoria = random.choice(list(PRODUCTOS_POR_CATEGORIA.keys()))
        base = random.choice(PRODUCTOS_POR_CATEGORIA[categoria])
        productos.append(
            {
                "id": i,
                "nombre": f"{base} {random.choice(ADJETIVOS)}",
                "categoria": categoria,
                # round(..., 2) deja el precio con dos decimales.
                "precio": round(random.uniform(49, 4999), 2),
                "stock": random.randint(0, 150),
                "fecha_alta": _fecha_aleatoria(),
            }
        )
    return productos


def generar_clientes(cantidad: int = 10) -> list[dict]:
    """Crea una lista de clientes inventados con correos únicos."""
    clientes = []
    for i in range(1, cantidad + 1):
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        # Agregamos el id al correo para garantizar que nunca se repita.
        correo = _quitar_acentos(f"{nombre}.{apellido}{i}@ejemplo.com").lower()
        clientes.append(
            {
                "id": i,
                "nombre": f"{nombre} {apellido}",
                "email": correo,
                "ciudad": random.choice(CIUDADES),
                "fecha_registro": _fecha_aleatoria(dias_atras=730),
            }
        )
    return clientes


# Este bloque permite probar el generador por sí solo:
#   python datos_sinteticos.py
if __name__ == "__main__":
    from pprint import pprint  # pprint imprime estructuras de forma legible

    pprint(generar_productos(3))
    pprint(generar_clientes(3))
