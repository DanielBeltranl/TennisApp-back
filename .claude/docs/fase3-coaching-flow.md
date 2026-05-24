# Fase 3 — Flujo entrenador-jugador
> Endpoints nuevos. Ningún endpoint anterior se modifica.

---

## Contexto

Un jugador busca a su entrenador, le manda una solicitud, y el entrenador la acepta asignándole un nivel. Hasta que eso ocurra, el jugador tiene `nivelUsuario: null` en su JWT.

**Reglas de negocio:**
- Un jugador puede tener **un solo entrenador**
- Un entrenador puede tener **muchos jugadores**
- No se puede enviar solicitud si ya tenés entrenador asignado
- No se puede enviar solicitud duplicada pendiente al mismo entrenador

---

## Flujo completo

```
JUGADOR                              ENTRENADOR
   |                                      |
   |-- GET /coaching/entrenadores/?q= --> busca
   |                                      |
   |-- POST /coaching/solicitudes/ -----> envía solicitud
   |                                      |
   |-- GET /coaching/solicitudes/         |
   |        enviadas/ -----------------> ve estado (PENDIENTE)
   |                                      |
   |                    GET /coaching/solicitudes/recibidas/
   |                                      |
   |                    PATCH /coaching/solicitudes/{id}/aceptar/
   |                                      |
   |-- GET /api/usuarios/perfil/ -------> verifica nivelUsuario != null
   |-- POST /api/token/refresh/ --------> refresca JWT con nuevo nivel
```

---

## Endpoints

### `GET /api/coaching/entrenadores/?q=nombre`
> Solo accesible para jugadores. Busca por nombre, apellido o correo.

**Ejemplo:** `GET /api/coaching/entrenadores/?q=martin`

**Response `200`**
```json
[
  {
    "id": 6,
    "nombre": "Martín",
    "apellidoPaterno": "López",
    "apellidoMaterno": "Silva",
    "correo": "martin@mail.com"
  }
]
```

> Devuelve array vacío `[]` si no hay resultados o si `q` no se envía.

---

### `POST /api/coaching/solicitudes/`
> Solo accesible para jugadores.

**Request**
```json
{
  "entrenador_id": 6
}
```

**Response `201`**
```json
{
  "id": 1,
  "jugador": {
    "id": 5,
    "nombre": "Carlos",
    "apellidoPaterno": "González",
    "apellidoMaterno": "Pérez",
    "correo": "carlos@mail.com"
  },
  "entrenador": {
    "id": 6,
    "nombre": "Martín",
    "apellidoPaterno": "López",
    "apellidoMaterno": "Silva",
    "correo": "martin@mail.com"
  },
  "status": "PENDIENTE",
  "created_at": "2026-05-23T14:00:00Z",
  "updated_at": "2026-05-23T14:00:00Z"
}
```

**Errores posibles**
```json
// Entrenador no encontrado
{ "entrenador_id": "Entrenador no encontrado." }

// Ya tenés entrenador
{ "non_field_errors": ["Ya tenés un entrenador asignado."] }

// Solicitud duplicada
{ "non_field_errors": ["Ya tenés una solicitud pendiente con este entrenador."] }
```

---

### `GET /api/coaching/solicitudes/enviadas/`
> Solo jugadores. Sirve para que el front muestre el estado de la solicitud.

**Response `200`**
```json
[
  {
    "id": 1,
    "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "apellidoMaterno": "Pérez", "correo": "carlos@mail.com" },
    "entrenador": { "id": 6, "nombre": "Martín", "apellidoPaterno": "López", "apellidoMaterno": "Silva", "correo": "martin@mail.com" },
    "status": "PENDIENTE",
    "created_at": "2026-05-23T14:00:00Z",
    "updated_at": "2026-05-23T14:00:00Z"
  }
]
```

**Valores de `status`:** `"PENDIENTE"` | `"ACEPTADA"` | `"RECHAZADA"`

---

### `GET /api/coaching/solicitudes/recibidas/`
> Solo entrenadores. Devuelve las solicitudes **pendientes**.

**Response `200`**
```json
[
  {
    "id": 1,
    "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "apellidoMaterno": "Pérez", "correo": "carlos@mail.com" },
    "entrenador": { "id": 6, "nombre": "Martín", "apellidoPaterno": "López", "apellidoMaterno": "Silva", "correo": "martin@mail.com" },
    "status": "PENDIENTE",
    "created_at": "2026-05-23T14:00:00Z",
    "updated_at": "2026-05-23T14:00:00Z"
  }
]
```

---

### `PATCH /api/coaching/solicitudes/{id}/aceptar/`
> Solo entrenadores. Asigna nivel al jugador y cierra la solicitud.

**Request**
```json
{
  "nivel": "Amateur"
}
```

**Valores válidos de `nivel`:** `"Amateur"` | `"Semi-Pro"` | `"Profesional"`

**Response `200`**
```json
{
  "id": 1,
  "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "apellidoMaterno": "Pérez", "correo": "carlos@mail.com" },
  "status": "ACEPTADA",
  "nivel_asignado": "Amateur"
}
```

**Errores posibles**
```json
// Solicitud no existe o no pertenece al entrenador
{ "error": "Solicitud no encontrada." }

// nivel inválido
{ "nivel": ["\"Experto\" is not a valid choice."] }
```

---

### `PATCH /api/coaching/solicitudes/{id}/rechazar/`
> Solo entrenadores. Sin body.

**Response `200`**
```json
{
  "id": 1,
  "status": "RECHAZADA"
}
```

**Error**
```json
{ "error": "Solicitud no encontrada." }
```

---

## Manejo del JWT post-aceptación

Cuando el entrenador acepta, el JWT del jugador **sigue teniendo `nivelUsuario: null`** hasta que refresque el token.

**Flujo recomendado para el front:**

```
1. Jugador ve banner "Sin nivel asignado"
2. Jugador consulta GET /api/coaching/solicitudes/enviadas/
3. Si status === "ACEPTADA" → llamar POST /api/token/refresh/ con el refresh token
4. Guardar el nuevo access token → el JWT ya trae nivelUsuario con el nivel asignado
5. Redirigir al dashboard normal
```

---

## Permisos por rol

| Endpoint | Jugador | Entrenador |
|----------|---------|------------|
| `GET /coaching/entrenadores/` | ✅ | ❌ |
| `POST /coaching/solicitudes/` | ✅ | ❌ |
| `GET /coaching/solicitudes/enviadas/` | ✅ | ❌ |
| `GET /coaching/solicitudes/recibidas/` | ❌ | ✅ |
| `PATCH /coaching/solicitudes/{id}/aceptar/` | ❌ | ✅ |
| `PATCH /coaching/solicitudes/{id}/rechazar/` | ❌ | ✅ |

> Intentar acceder con el rol incorrecto devuelve `403 Forbidden`.
