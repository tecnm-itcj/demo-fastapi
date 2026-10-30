# Diagramas de secuencia de la Demo Tienda API

Este documento muestra, paso a paso, **qué pasa por dentro** cuando la API arranca y cuando recibe una petición. Los diagramas están escritos en [Mermaid](https://mermaid.js.org/), así que GitHub los dibuja automáticamente.

## Participantes

| Participante | Qué es en el proyecto |
|---|---|
| **Cliente** | Quien hace la petición: el navegador, `/docs`, `curl`, Postman o un programa en Python. |
| **Uvicorn** | El servidor que escucha en `http://127.0.0.1:8000` y le pasa cada petición a FastAPI. |
| **FastAPI** | El objeto `app` de `main.py`. Busca la ruta que coincide con el método y la URL. |
| **Pydantic** | Valida los datos de entrada (parámetros y body) y da forma a la respuesta (`response_model`). |
| **Ruta** | La función de Python decorada con `@app.get` o `@app.post` (por ejemplo `crear_producto`). |
| **Memoria** | Las listas `PRODUCTOS` y `CLIENTES`, que hacen el papel de base de datos. |
| **datos_sinteticos** | El módulo `datos_sinteticos.py`, que inventa los datos iniciales. |

---

## 1. Arranque del servidor

Sucede una sola vez, al ejecutar `uvicorn main:app --reload`.

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Desarrollador
    participant U as Uvicorn
    participant M as main.py
    participant DS as datos_sinteticos
    participant Mem as Memoria (PRODUCTOS / CLIENTES)

    Dev->>U: uvicorn main:app --reload
    U->>M: importa el módulo main
    M->>DS: from datos_sinteticos import ...
    Note over DS: random.seed(42)<br/>siempre los mismos datos
    M->>M: app = FastAPI(title, description, version)
    M->>M: HORA_INICIO = datetime.now(UTC)
    M->>DS: generar_productos(cantidad=25)
    DS-->>M: lista de 25 productos
    M->>Mem: PRODUCTOS = [...]
    M->>DS: generar_clientes(cantidad=15)
    DS-->>M: lista de 15 clientes
    M->>Mem: CLIENTES = [...]
    M->>M: registra rutas (@app.get / @app.post)
    M-->>U: objeto app listo
    U-->>Dev: Uvicorn running on http://127.0.0.1:8000
```

---

## 2. Flujo general de cualquier petición

Todas las rutas siguen este mismo esqueleto. Los siguientes diagramas solo detallan lo que cambia en cada caso.

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant U as Uvicorn
    participant F as FastAPI
    participant P as Pydantic
    participant R as Ruta (función)
    participant Mem as Memoria

    C->>U: Petición HTTP (método + URL + body)
    U->>F: entrega la petición (ASGI)
    F->>F: busca la ruta que coincide
    alt No existe la ruta
        F-->>U: 404 {"detail": "Not Found"}
    else Ruta encontrada
        F->>P: valida parámetros de ruta, query y body
        alt Datos inválidos
            P-->>F: errores de validación
            F-->>U: 422 Unprocessable Entity
        else Datos válidos
            F->>R: llama a la función con los datos ya convertidos
            R->>Mem: lee o modifica la lista
            Mem-->>R: datos
            alt Regla de negocio falla
                R-->>F: raise HTTPException(404 / 409)
                F-->>U: 404 o 409 {"detail": "..."}
            else Todo bien
                R-->>F: dict o lista
                F->>P: aplica response_model (filtra y valida)
                P-->>F: datos listos
                F-->>U: 200 / 201 + JSON
            end
        end
    end
    U-->>C: Respuesta HTTP
```

---

## 3. `GET /health` (Health Check)

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente / Monitoreo
    participant F as FastAPI
    participant R as health_check()
    participant Mem as Memoria
    participant P as Pydantic

    C->>F: GET /health
    F->>R: health_check()
    R->>R: ahora = datetime.now(UTC)
    R->>R: segundos_activo = ahora - HORA_INICIO
    R->>Mem: len(PRODUCTOS), len(CLIENTES)
    Mem-->>R: 25, 15
    R->>P: EstadoSalud(estado="ok", ...)
    P-->>F: modelo validado
    F-->>C: 200 OK {"estado": "ok", "segundos_activo": ..., ...}
```

---

## 4. `GET /productos` (listar con filtros)

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant F as FastAPI
    participant P as Pydantic
    participant R as listar_productos()
    participant Mem as PRODUCTOS

    C->>F: GET /productos?categoria=Hogar&precio_max=500&limite=5
    F->>P: valida query (precio_max > 0, 1 <= limite <= 100)
    alt Query inválida (ej. limite=0)
        P-->>F: error
        F-->>C: 422 Unprocessable Entity
    else Query válida
        F->>R: listar_productos("Hogar", 500.0, 5)
        R->>Mem: lee la lista completa
        Mem-->>R: 25 productos
        opt categoria enviada
            R->>R: filtra por categoría (sin importar mayúsculas)
        end
        opt precio_max enviado
            R->>R: filtra precio <= precio_max
        end
        R->>R: resultado[:limite]
        R-->>F: lista de productos
        F->>P: response_model = list[Producto]
        F-->>C: 200 OK [ {...}, {...} ]
    end
```

`GET /clientes?ciudad=...` sigue exactamente el mismo flujo, con un solo filtro opcional por ciudad.

---

## 5. `GET /productos/{producto_id}` (consultar uno)

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant F as FastAPI
    participant P as Pydantic
    participant R as obtener_producto()
    participant Mem as PRODUCTOS

    C->>F: GET /productos/3
    F->>P: convierte "3" a int
    alt No es número (ej. /productos/abc)
        F-->>C: 422 Unprocessable Entity
    else Es número
        F->>R: obtener_producto(3)
        R->>Mem: recorre la lista buscando id == 3
        alt Lo encuentra
            Mem-->>R: producto
            R-->>F: producto
            F-->>C: 200 OK {"id": 3, ...}
        else No lo encuentra
            R-->>F: raise HTTPException(404)
            F-->>C: 404 {"detail": "No existe un producto con id 3"}
        end
    end
```

`GET /clientes/{cliente_id}` funciona igual, solo que usa `next(...)` para buscar.

---

## 6. `POST /productos` (crear)

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant F as FastAPI
    participant P as Pydantic
    participant R as crear_producto()
    participant Mem as PRODUCTOS

    C->>F: POST /productos + JSON {nombre, categoria, precio, stock}
    F->>P: valida body con ProductoCrear
    alt Falta un campo o no cumple reglas (precio <= 0, stock < 0, nombre corto)
        P-->>F: errores de validación
        F-->>C: 422 Unprocessable Entity
    else Body válido
        P-->>F: objeto ProductoCrear
        F->>R: crear_producto(nuevo)
        R->>Mem: max(id) + 1
        Mem-->>R: siguiente_id
        R->>R: arma dict {id, **nuevo.model_dump(), fecha_alta}
        R->>Mem: PRODUCTOS.append(producto)
        R-->>F: producto
        F->>P: response_model = Producto
        F-->>C: 201 Created {"id": 26, ...}
    end
```

---

## 7. `POST /clientes` (registrar, con correo único)

Este es el único flujo con una **regla de negocio** propia: el correo no se puede repetir.

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant F as FastAPI
    participant P as Pydantic
    participant R as crear_cliente()
    participant Mem as CLIENTES

    C->>F: POST /clientes + JSON {nombre, email, ciudad}
    F->>P: valida body con ClienteCrear (EmailStr)
    alt Correo con formato inválido o faltan campos
        F-->>C: 422 Unprocessable Entity
    else Body válido
        F->>R: crear_cliente(nuevo)
        R->>Mem: ¿existe un cliente con ese email?
        alt Ya existe
            Mem-->>R: sí
            R-->>F: raise HTTPException(409)
            F-->>C: 409 Conflict {"detail": "Ya existe un cliente con el correo ..."}
        else No existe
            Mem-->>R: no
            R->>Mem: max(id) + 1
            R->>R: arma dict {id, **nuevo.model_dump(), fecha_registro}
            R->>Mem: CLIENTES.append(cliente)
            R-->>F: cliente
            F-->>C: 201 Created {"id": 16, ...}
        end
    end
```

---

## Resumen de códigos de respuesta por ruta

| Ruta | Éxito | Errores posibles |
|---|---|---|
| `GET /` | 200 | |
| `GET /health` | 200 | |
| `GET /productos` | 200 | 422 |
| `GET /productos/{id}` | 200 | 404, 422 |
| `POST /productos` | 201 | 422 |
| `GET /clientes` | 200 | |
| `GET /clientes/{id}` | 200 | 404, 422 |
| `POST /clientes` | 201 | 409, 422 |
