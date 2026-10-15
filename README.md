# Demo Tienda API con FastAPI

Backend de ejemplo hecho con **FastAPI** para aprender, paso a paso, cómo se construye una API REST en Python. Sirve **datos sintéticos** (inventados) de una pequeña tienda: productos y clientes.

> Está pensado para alumnos que nunca han usado FastAPI. Lee este documento de principio a fin y después abre `main.py`: cada línea importante está comentada.

---

## Tabla de contenido

1. [¿Qué vas a aprender?](#1-qué-vas-a-aprender)
2. [Conceptos básicos antes de empezar](#2-conceptos-básicos-antes-de-empezar)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Instalación en tu laptop](#4-instalación-en-tu-laptop)
5. [Ejecutar la API](#5-ejecutar-la-api)
6. [Rutas disponibles](#6-rutas-disponibles)
7. [Cómo probar la API](#7-cómo-probar-la-api)
8. [Explicación del código](#8-explicación-del-código)
9. [Pruebas automáticas](#9-pruebas-automáticas)
10. [Problemas comunes](#10-problemas-comunes)
11. [Ejercicios propuestos](#11-ejercicios-propuestos)

---

## 1. ¿Qué vas a aprender?

- Crear un entorno virtual (`.venv`) e instalar dependencias con `requirements.txt`.
- Levantar un servidor con **Uvicorn**.
- Definir rutas **GET** (leer datos) y **POST** (crear datos).
- Usar **parámetros de ruta** (`/productos/3`) y **parámetros de consulta** (`/productos?limite=5`).
- Validar datos automáticamente con **Pydantic**.
- Responder errores HTTP correctos (404, 409, 422).
- Crear una ruta de **Health Check**.
- Usar la documentación interactiva que FastAPI genera sola (`/docs`).

---

## 2. Conceptos básicos antes de empezar

| Concepto | Explicación sencilla |
|---|---|
| **API** | Un programa que recibe peticiones y responde datos (normalmente en JSON). Otros programas, como una app web o móvil, la consumen. |
| **REST** | Un estilo para diseñar APIs usando URLs (recursos) y métodos HTTP (acciones). |
| **GET** | Método HTTP para **leer** información. No modifica nada. |
| **POST** | Método HTTP para **crear** información nueva. Los datos viajan en el *body* (cuerpo) de la petición. |
| **JSON** | Formato de texto para intercambiar datos: `{"nombre": "Ana", "edad": 20}`. |
| **Código de estado** | Número que indica el resultado: `200` OK, `201` creado, `404` no encontrado, `409` conflicto, `422` datos inválidos. |
| **FastAPI** | Framework de Python para crear APIs rápido, con validación y documentación automáticas. |
| **Uvicorn** | El servidor que "escucha" en un puerto y le pasa las peticiones a FastAPI. |
| **Pydantic** | Librería que valida que los datos tengan el tipo y la forma correcta. |
| **Entorno virtual** | Una carpeta aislada con su propio Python y sus propias librerías, para que cada proyecto no choque con los demás. |
| **Datos sintéticos** | Datos inventados por un programa que parecen reales. Ideales para demos. |

---

## 3. Estructura del proyecto

```
demo-fastapi/
├── main.py               # La API: modelos, rutas y lógica (archivo principal)
├── datos_sinteticos.py   # Genera los productos y clientes inventados
├── test_main.py          # Pruebas automáticas con pytest
├── requirements.txt      # Lista de librerías que necesita el proyecto
├── .gitignore            # Archivos que Git debe ignorar (por ejemplo .venv)
└── README.md             # Este documento
```

---

## 4. Instalación en tu laptop

### 4.1 Requisitos previos

- **Python 3.10 o superior.** Verifica tu versión:

  ```bash
  python --version
  ```

  En macOS o Linux a veces el comando es `python3`. Si `python --version` no funciona, usa `python3` en todos los pasos.

  Si no tienes Python, descárgalo de [python.org](https://www.python.org/downloads/). En Windows, **marca la casilla "Add Python to PATH"** durante la instalación.

- Una terminal:
  - **Windows:** PowerShell o "Símbolo del sistema" (CMD).
  - **macOS:** la app Terminal.
  - **Linux:** tu terminal favorita.

### 4.2 Descomprimir el proyecto y entrar a la carpeta

Descomprime el archivo `demo-fastapi.zip` y entra a la carpeta desde la terminal:

```bash
cd ruta/donde/descomprimiste/demo-fastapi
```

Comprueba que estás en el lugar correcto listando los archivos (`dir` en Windows, `ls` en macOS/Linux). Debes ver `main.py` y `requirements.txt`.

### 4.3 Crear el entorno virtual (`.venv`)

Este comando crea una carpeta llamada `.venv` con un Python aislado solo para este proyecto:

**Windows:**
```powershell
python -m venv .venv
```

**macOS / Linux:**
```bash
python3 -m venv .venv
```

¿Qué significa?
- `python -m venv` ejecuta el módulo `venv`, que viene incluido con Python.
- `.venv` es el nombre de la carpeta que se va a crear. El punto inicial es una convención para indicar que es una carpeta "de configuración".

### 4.4 Activar el entorno virtual

Activarlo hace que, en esa terminal, `python` y `pip` usen el entorno del proyecto y no el de tu sistema.

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Sabrás que funcionó porque tu terminal mostrará `(.venv)` al inicio de la línea:

```
(.venv) C:\Users\alumno\demo-fastapi>
```

> **Windows: error "la ejecución de scripts está deshabilitada".** Ejecuta una sola vez en PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> y vuelve a intentar activar el entorno.

**Importante:** cada vez que abras una terminal nueva para trabajar en el proyecto, tienes que volver a activar el entorno. Para desactivarlo escribe `deactivate`.

### 4.5 Actualizar pip (recomendado)

`pip` es el instalador de paquetes de Python. Conviene tenerlo actualizado:

```bash
python -m pip install --upgrade pip
```

### 4.6 Instalar las dependencias con `requirements.txt`

El archivo `requirements.txt` contiene la lista de librerías que el proyecto necesita. Con un solo comando las instalas todas dentro del `.venv`:

```bash
pip install -r requirements.txt
```

- `-r` significa "lee la lista desde este archivo".

Contenido de `requirements.txt`:

| Paquete | Para qué sirve |
|---|---|
| `fastapi` | El framework para construir la API. |
| `uvicorn[standard]` | El servidor que ejecuta la API. `[standard]` agrega extras como la recarga automática. |
| `email-validator` | Permite validar correos electrónicos con el tipo `EmailStr`. |
| `pytest` | Para ejecutar las pruebas automáticas. |
| `httpx` | Lo usa el cliente de pruebas de FastAPI para simular peticiones. |

Verifica la instalación:

```bash
pip list
```

Deberías ver `fastapi`, `uvicorn`, `pydantic`, entre otros.

> **Tip:** si algún día agregas una librería nueva al proyecto, puedes guardar la lista exacta de lo instalado con `pip freeze > requirements.txt`.

### 4.7 Resumen rápido (todos los comandos)

**Windows (PowerShell):**
```powershell
cd demo-fastapi
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

**macOS / Linux:**
```bash
cd demo-fastapi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 5. Ejecutar la API

Con el entorno virtual **activado**, ejecuta:

```bash
uvicorn main:app --reload
```

Desglose del comando:
- `uvicorn`: el servidor.
- `main`: el archivo `main.py` (sin la extensión).
- `app`: la variable `app = FastAPI(...)` dentro de ese archivo.
- `--reload`: reinicia el servidor solo cada vez que guardas un cambio en el código. Úsalo **solo en desarrollo**.

Verás algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Abre en tu navegador:

| URL | Qué verás |
|---|---|
| http://127.0.0.1:8000 | Mensaje de bienvenida |
| http://127.0.0.1:8000/docs | **Documentación interactiva (Swagger UI)**. Aquí puedes probar todas las rutas con botones. |
| http://127.0.0.1:8000/redoc | Documentación alternativa (ReDoc), más cómoda para leer. |

Para detener el servidor presiona `Ctrl + C` en la terminal.

**Alternativa:** también puedes ejecutar `python main.py`, porque el archivo tiene un bloque `if __name__ == "__main__":` que arranca Uvicorn.

---

## 6. Rutas disponibles

| Método | Ruta | Descripción | Respuesta exitosa |
|---|---|---|---|
| GET | `/` | Bienvenida | 200 |
| GET | `/health` | **Health Check**: estado del servidor | 200 |
| GET | `/productos` | Lista productos. Filtros opcionales: `categoria`, `precio_max`, `limite` | 200 |
| GET | `/productos/{producto_id}` | Un producto por id | 200 (o 404) |
| POST | `/productos` | Crea un producto | 201 (o 422) |
| GET | `/clientes` | Lista clientes. Filtro opcional: `ciudad` | 200 |
| GET | `/clientes/{cliente_id}` | Un cliente por id | 200 (o 404) |
| POST | `/clientes` | Registra un cliente (correo único) | 201 (o 409, 422) |

Categorías de productos disponibles: `Electrónica`, `Hogar`, `Deportes`, `Papelería`.

### Ejemplo de respuesta de `/health`

```json
{
  "estado": "ok",
  "hora_servidor": "2026-10-15T12:57:26.697687+00:00",
  "segundos_activo": 2,
  "total_productos": 25,
  "total_clientes": 15
}
```

### ¿Para qué sirve un Health Check?

Es una ruta muy simple que responde `200 OK` si el servicio está vivo. Herramientas como Docker, Kubernetes, balanceadores de carga o sistemas de monitoreo la consultan cada pocos segundos. Si deja de responder, saben que deben reiniciar el servicio o mandar una alerta.

---

## 7. Cómo probar la API

### Opción A: desde `/docs` (la más fácil)

1. Abre http://127.0.0.1:8000/docs
2. Da clic en una ruta, por ejemplo `POST /productos`.
3. Da clic en **"Try it out"**.
4. Edita el JSON de ejemplo y da clic en **"Execute"**.
5. Abajo verás la respuesta y el código de estado.

### Opción B: desde la terminal con `curl`

Abre **otra** terminal (deja la del servidor corriendo).

```bash
# Health check
curl http://127.0.0.1:8000/health

# Listar 5 productos de la categoría Hogar
curl "http://127.0.0.1:8000/productos?categoria=Hogar&limite=5"

# Consultar el producto con id 3
curl http://127.0.0.1:8000/productos/3

# Crear un producto (POST con JSON en el body)
curl -X POST http://127.0.0.1:8000/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Termo Eco", "categoria": "Hogar", "precio": 299.5, "stock": 8}'

# Registrar un cliente
curl -X POST http://127.0.0.1:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana Ruiz", "email": "ana@ejemplo.com", "ciudad": "Puebla"}'
```

> **Windows (PowerShell):** `curl` puede comportarse distinto. Usa `curl.exe` en lugar de `curl`, o mejor prueba desde `/docs`. También puedes usar:
> ```powershell
> Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/productos `
>   -ContentType "application/json" `
>   -Body '{"nombre": "Termo Eco", "categoria": "Hogar", "precio": 299.5, "stock": 8}'
> ```

### Opción C: desde Python

```python
import httpx

r = httpx.get("http://127.0.0.1:8000/productos", params={"limite": 3})
print(r.status_code, r.json())
```

### Prueba los errores a propósito

| Qué hacer | Qué pasa |
|---|---|
| `GET /productos/9999` | 404: el producto no existe |
| `GET /productos/abc` | 422: el id debe ser número |
| `POST /productos` con `"precio": -10` | 422: Pydantic exige precio mayor que 0 |
| `POST /clientes` con un correo inválido como `"hola"` | 422: no es un correo válido |
| `POST /clientes` dos veces con el mismo correo | 409: correo duplicado |

---

## 8. Explicación del código

### 8.1 Crear la aplicación

```python
from fastapi import FastAPI

app = FastAPI(title="Demo Tienda API", version="1.0.0")
```

`app` es el corazón del proyecto. Uvicorn la busca cuando ejecutas `uvicorn main:app`.

### 8.2 Definir una ruta GET

```python
@app.get("/health")
def health_check():
    return {"estado": "ok"}
```

- La línea con `@` es un **decorador**: le dice a FastAPI "cuando llegue un GET a `/health`, ejecuta esta función".
- Lo que la función regresa se convierte automáticamente a JSON.

### 8.3 Parámetros de ruta y de consulta

```python
@app.get("/productos/{producto_id}")      # parámetro de RUTA
def obtener_producto(producto_id: int):
    ...

@app.get("/productos")
def listar_productos(limite: int = 10):   # parámetro de CONSULTA (?limite=5)
    ...
```

- Si el nombre aparece entre `{llaves}` en la URL, es parámetro de **ruta**.
- Si no aparece en la URL, FastAPI lo busca en la **query string** (`?clave=valor`).
- El tipo (`int`) hace que FastAPI convierta y valide el valor automáticamente.

### 8.4 Modelos con Pydantic y rutas POST

```python
from pydantic import BaseModel, Field

class ProductoCrear(BaseModel):
    nombre: str
    precio: float = Field(..., gt=0)   # obligatorio y mayor que 0

@app.post("/productos", status_code=201)
def crear_producto(nuevo: ProductoCrear):
    ...
```

- Como `nuevo` es un modelo de Pydantic, FastAPI sabe que debe leerlo del **body** en JSON.
- Si falta un campo o un valor no cumple las reglas, FastAPI responde **422** sin que tú escribas una sola validación.
- Se usan dos modelos: `ProductoCrear` (lo que envía el usuario, sin `id`) y `Producto` (lo que devuelve la API, con `id` y fecha generados por el servidor).

### 8.5 Manejo de errores

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="No existe un producto con id 9")
```

FastAPI convierte la excepción en una respuesta `{"detail": "..."}` con el código indicado.

### 8.6 Datos sintéticos

`datos_sinteticos.py` usa el módulo `random` de Python para combinar nombres, categorías, precios y ciudades al azar. Usa `random.seed(42)` para que **todos obtengan los mismos datos** cada vez que arranca el servidor.

Los datos se guardan en **listas en memoria**. Esto significa que:
- Los registros que crees con POST **se pierden al reiniciar** el servidor.
- En un proyecto real se reemplazarían por una base de datos (PostgreSQL, MySQL, SQLite, etc.).

Puedes ver ejemplos de los datos generados con:

```bash
python datos_sinteticos.py
```

---

## 9. Pruebas automáticas

El archivo `test_main.py` revisa que la API funcione: health check, filtros, errores 404/409/422 y creación de registros. Ejecútalas con el entorno activado:

```bash
pytest -v
```

Resultado esperado: `6 passed`. Si ves un aviso (*warning*) sobre `httpx`, es informativo y no afecta las pruebas.

---

## 10. Problemas comunes

| Problema | Solución |
|---|---|
| `python` no se reconoce como comando | Usa `python3` o `py` (Windows), o reinstala Python marcando "Add Python to PATH". |
| `ModuleNotFoundError: No module named 'fastapi'` | No activaste el `.venv` o no instalaste dependencias. Activa el entorno y ejecuta `pip install -r requirements.txt`. |
| `uvicorn` no se reconoce | Mismo caso: activa el entorno. También puedes usar `python -m uvicorn main:app --reload`. |
| `Address already in use` / puerto 8000 ocupado | Ya hay un servidor corriendo. Ciérralo o usa otro puerto: `uvicorn main:app --reload --port 8001`. |
| `Error loading ASGI app. Could not import module "main"` | Ejecutaste el comando fuera de la carpeta del proyecto. Entra con `cd` a la carpeta que contiene `main.py`. |
| En PowerShell no se puede activar el entorno | Ver la nota de `Set-ExecutionPolicy` en la sección 4.4. |
| Los productos que creé desaparecieron | Es normal: los datos viven en memoria y se reinician con el servidor. |

---

## 11. Ejercicios propuestos

1. **Fácil:** agrega a `GET /productos` un filtro `precio_min`.
2. **Fácil:** crea `GET /categorias` que devuelva la lista de categorías sin repetir.
3. **Medio:** agrega `PUT /productos/{producto_id}` para actualizar un producto completo.
4. **Medio:** agrega `DELETE /clientes/{cliente_id}` que responda `204 No Content`.
5. **Medio:** crea un recurso nuevo `pedidos` con `POST /pedidos` que valide que el cliente y el producto existan y que haya stock suficiente (descuéntalo al crear el pedido).
6. **Reto:** reemplaza las listas en memoria por una base de datos SQLite usando SQLModel o SQLAlchemy.

Escribe una prueba en `test_main.py` por cada ejercicio que resuelvas.

---

## Recursos para seguir aprendiendo

- Documentación oficial de FastAPI (en español): https://fastapi.tiangolo.com/es/
- Documentación de Pydantic: https://docs.pydantic.dev/
- Documentación de Uvicorn: https://www.uvicorn.org/
