"""
=====================================================================
 DEMO DE BACKEND CON FASTAPI
=====================================================================
Este archivo contiene una API completa y funcional hecha con FastAPI.
Está pensada para aprender, así que cada bloque tiene comentarios que
explican QUÉ hace y POR QUÉ se hace así.

Temática del demo: una pequeña tienda en línea con
  * Productos  (GET para listar/consultar, POST para crear)
  * Clientes   (GET para listar/consultar, POST para crear)
  * Health Check (para saber si el servidor está vivo)

Cómo ejecutarlo (con el entorno virtual activado):
    uvicorn main:app --reload

Luego abre en tu navegador:
    http://127.0.0.1:8000/docs   <- documentación interactiva (Swagger)
    http://127.0.0.1:8000/redoc  <- documentación alternativa (ReDoc)
=====================================================================
"""

# ---------------------------------------------------------------------
# 1) IMPORTACIONES
# ---------------------------------------------------------------------
# "datetime" nos sirve para registrar fechas y horas (por ejemplo, a qué
# hora arrancó el servidor o cuándo se creó un registro).
from datetime import datetime, timezone

# "Optional" indica que un valor puede existir o ser None (vacío).
from typing import Optional

# De FastAPI importamos:
#   FastAPI        -> la clase principal con la que creamos la aplicación.
#   HTTPException  -> para responder errores HTTP (por ejemplo 404 "no encontrado").
#   Query          -> para describir y validar parámetros que van en la URL (?clave=valor).
#   status         -> constantes con los códigos HTTP (200, 201, 404...) con nombres legibles.
from fastapi import FastAPI, HTTPException, Query, status

# Pydantic es la librería que FastAPI usa para VALIDAR datos.
#   BaseModel -> clase base para definir la "forma" de los datos (un esquema).
#   Field     -> permite agregar reglas (mínimos, máximos, ejemplos, descripciones).
#   EmailStr  -> tipo especial que valida que un texto sea un correo válido.
from pydantic import BaseModel, EmailStr, Field

# Importamos los datos sintéticos (falsos pero realistas) desde otro archivo.
# Separar los datos del código de la API es una buena práctica: así cada
# archivo tiene una sola responsabilidad.
from datos_sinteticos import generar_clientes, generar_productos

# ---------------------------------------------------------------------
# 2) CREACIÓN DE LA APLICACIÓN
# ---------------------------------------------------------------------
# "app" es el objeto central. Uvicorn (el servidor) lo busca por este
# nombre cuando ejecutamos:  uvicorn main:app
#   main -> nombre del archivo (main.py)
#   app  -> nombre de la variable de abajo
# Los textos que pasamos (title, description, version) aparecen en /docs.
app = FastAPI(
    title="Demo Tienda API",
    description=(
        "API de ejemplo para aprender FastAPI. "
        "Sirve datos sintéticos de productos y clientes."
    ),
    version="1.0.0",
)

# Guardamos la hora en que arrancó el servidor para reportarla en el
# Health Check (así sabemos cuánto tiempo lleva encendido).
HORA_INICIO = datetime.now(timezone.utc)

# ---------------------------------------------------------------------
# 3) "BASE DE DATOS" EN MEMORIA
# ---------------------------------------------------------------------
# En un proyecto real usarías una base de datos (PostgreSQL, MySQL, etc.).
# Para el demo guardamos los datos en listas de Python. OJO: como viven
# en memoria, si reinicias el servidor se pierden los registros nuevos y
# se vuelven a generar los datos sintéticos originales.
PRODUCTOS: list[dict] = generar_productos(cantidad=25)
CLIENTES: list[dict] = generar_clientes(cantidad=15)


# ---------------------------------------------------------------------
# 4) MODELOS (ESQUEMAS) CON PYDANTIC
# ---------------------------------------------------------------------
# Un modelo describe la estructura de los datos. FastAPI los usa para:
#   a) VALIDAR lo que llega en un POST (si falta un campo o el tipo es
#      incorrecto, responde automáticamente un error 422).
#   b) FILTRAR y documentar lo que devolvemos en las respuestas.
#   c) Generar la documentación automática en /docs.
#
# Patrón común: un modelo "...Crear" (lo que manda el cliente, SIN id)
# y otro modelo completo (lo que devuelve la API, CON id generado).


class ProductoCrear(BaseModel):
    """Datos que el cliente debe enviar para crear un producto."""

    # Field(...) con "..." significa que el campo es OBLIGATORIO.
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Audífonos Bluetooth"])
    categoria: str = Field(..., examples=["Electrónica"])
    # gt=0 -> "greater than 0": el precio debe ser mayor que cero.
    precio: float = Field(..., gt=0, examples=[799.90])
    # ge=0 -> "greater or equal": el stock puede ser 0 pero no negativo.
    stock: int = Field(..., ge=0, examples=[10])


class Producto(ProductoCrear):
    """Producto completo, tal como lo devuelve la API.

    Hereda todos los campos de ProductoCrear y agrega los que genera el
    servidor (id y fecha de alta).
    """

    id: int
    fecha_alta: str


class ClienteCrear(BaseModel):
    """Datos que el cliente debe enviar para registrar un cliente."""

    nombre: str = Field(..., min_length=2, examples=["María López"])
    # EmailStr valida automáticamente que tenga formato de correo.
    email: EmailStr = Field(..., examples=["maria.lopez@ejemplo.com"])
    ciudad: str = Field(..., examples=["Guadalajara"])


class Cliente(ClienteCrear):
    """Cliente completo, tal como lo devuelve la API."""

    id: int
    fecha_registro: str


class EstadoSalud(BaseModel):
    """Respuesta del Health Check."""

    estado: str
    hora_servidor: str
    segundos_activo: int
    total_productos: int
    total_clientes: int


# ---------------------------------------------------------------------
# 5) RUTAS (ENDPOINTS)
# ---------------------------------------------------------------------
# Una "ruta" combina un MÉTODO HTTP + una URL. Se declara con un
# decorador (la línea que empieza con @) encima de una función.
#
#   @app.get("/algo")   -> responde a peticiones GET  (leer datos)
#   @app.post("/algo")  -> responde a peticiones POST (crear datos)
#
# Lo que la función regresa (dict, lista, modelo) FastAPI lo convierte
# automáticamente a JSON.
#
# "tags" agrupa las rutas en secciones dentro de /docs.
# "response_model" le dice a FastAPI qué forma tiene la respuesta, para
# validarla y documentarla.


# ----------------------------- RAÍZ ----------------------------------
@app.get("/", tags=["General"])
def inicio():
    """Ruta de bienvenida. Útil para comprobar rápido que la API responde."""
    return {
        "mensaje": "Bienvenido a la Demo Tienda API",
        "documentacion": "/docs",
        "health_check": "/health",
    }


# ------------------------- HEALTH CHECK ------------------------------
# Un Health Check es una ruta muy simple que herramientas externas
# (Docker, Kubernetes, balanceadores de carga, monitoreo) consultan
# periódicamente. Si responde 200 OK, el servicio está "sano".
@app.get("/health", response_model=EstadoSalud, tags=["General"])
def health_check():
    """Indica si el servidor está funcionando y muestra datos básicos."""
    ahora = datetime.now(timezone.utc)
    return EstadoSalud(
        estado="ok",
        hora_servidor=ahora.isoformat(),
        segundos_activo=int((ahora - HORA_INICIO).total_seconds()),
        total_productos=len(PRODUCTOS),
        total_clientes=len(CLIENTES),
    )


# --------------------------- PRODUCTOS -------------------------------
@app.get("/productos", response_model=list[Producto], tags=["Productos"])
def listar_productos(
    # Estos parámetros NO están en la ruta, así que FastAPI los toma de
    # la "query string". Ejemplo de URL:
    #   /productos?categoria=Hogar&precio_max=500&limite=5
    # Optional[...] = None significa que el parámetro es opcional.
    categoria: Optional[str] = Query(None, description="Filtra por categoría exacta"),
    precio_max: Optional[float] = Query(None, gt=0, description="Precio máximo"),
    limite: int = Query(10, ge=1, le=100, description="Cuántos resultados devolver"),
):
    """Devuelve la lista de productos, con filtros opcionales."""
    resultado = PRODUCTOS

    # Aplicamos cada filtro solo si el usuario lo envió.
    if categoria:
        # .lower() hace la comparación sin importar mayúsculas/minúsculas.
        resultado = [p for p in resultado if p["categoria"].lower() == categoria.lower()]
    if precio_max is not None:
        resultado = [p for p in resultado if p["precio"] <= precio_max]

    # Rebanamos la lista para respetar el límite (paginación sencilla).
    return resultado[:limite]


# "{producto_id}" entre llaves es un PARÁMETRO DE RUTA: forma parte de la
# URL. Ejemplo: /productos/3  -> producto_id = 3
# Como la función declara "producto_id: int", FastAPI convierte el texto
# "3" a número entero y, si alguien manda /productos/abc, responde 422.
@app.get("/productos/{producto_id}", response_model=Producto, tags=["Productos"])
def obtener_producto(producto_id: int):
    """Devuelve un solo producto buscándolo por su id."""
    for producto in PRODUCTOS:
        if producto["id"] == producto_id:
            return producto

    # Si el ciclo terminó sin encontrarlo, lanzamos un error 404.
    # FastAPI lo convierte en la respuesta JSON: {"detail": "..."}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe un producto con id {producto_id}",
    )


# status_code=201 ("Created") es el código correcto cuando un POST
# crea un recurso nuevo (por defecto FastAPI usaría 200).
@app.post(
    "/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
)
def crear_producto(nuevo: ProductoCrear):
    """Crea un producto nuevo.

    El parámetro "nuevo" es de tipo ProductoCrear (un modelo Pydantic),
    por eso FastAPI sabe que debe leerlo del CUERPO (body) de la petición
    en formato JSON y validarlo antes de entrar a esta función.
    """
    # Generamos el siguiente id: el mayor existente + 1.
    siguiente_id = max((p["id"] for p in PRODUCTOS), default=0) + 1

    # .model_dump() convierte el modelo Pydantic a un diccionario normal.
    # Con ** "desempacamos" ese diccionario dentro del nuevo.
    producto = {
        "id": siguiente_id,
        **nuevo.model_dump(),
        "fecha_alta": datetime.now(timezone.utc).date().isoformat(),
    }
    PRODUCTOS.append(producto)
    return producto


# ---------------------------- CLIENTES -------------------------------
@app.get("/clientes", response_model=list[Cliente], tags=["Clientes"])
def listar_clientes(
    ciudad: Optional[str] = Query(None, description="Filtra por ciudad"),
):
    """Devuelve la lista de clientes, opcionalmente filtrada por ciudad."""
    if ciudad:
        return [c for c in CLIENTES if c["ciudad"].lower() == ciudad.lower()]
    return CLIENTES


@app.get("/clientes/{cliente_id}", response_model=Cliente, tags=["Clientes"])
def obtener_cliente(cliente_id: int):
    """Devuelve un solo cliente por su id."""
    # next(...) devuelve el primer elemento que cumpla la condición, o
    # None si ninguno la cumple. Es otra forma de hacer la búsqueda.
    cliente = next((c for c in CLIENTES if c["id"] == cliente_id), None)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un cliente con id {cliente_id}",
        )
    return cliente


@app.post(
    "/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
    tags=["Clientes"],
)
def crear_cliente(nuevo: ClienteCrear):
    """Registra un cliente nuevo. No permite correos duplicados."""
    # Regla de negocio: el correo debe ser único.
    if any(c["email"].lower() == nuevo.email.lower() for c in CLIENTES):
        # 409 Conflict: el recurso choca con uno que ya existe.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cliente con el correo {nuevo.email}",
        )

    siguiente_id = max((c["id"] for c in CLIENTES), default=0) + 1
    cliente = {
        "id": siguiente_id,
        **nuevo.model_dump(),
        "fecha_registro": datetime.now(timezone.utc).date().isoformat(),
    }
    CLIENTES.append(cliente)
    return cliente


# ---------------------------------------------------------------------
# 6) EJECUCIÓN DIRECTA (OPCIONAL)
# ---------------------------------------------------------------------
# Este bloque solo se ejecuta si corres:  python main.py
# Es una alternativa a escribir el comando de uvicorn en la terminal.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
