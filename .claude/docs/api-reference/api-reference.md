# TennisApp — API Reference para Frontend

## Base URL

```
http://localhost:8000/api
```

## Autenticación

Todos los endpoints (excepto `registro` y `login`) requieren el header:

```
Authorization: Bearer <access_token>
```

El `access_token` se obtiene al hacer login o registro. Expira en **60 minutos**.
Usa el `refresh_token` para obtener uno nuevo sin volver a loguearse.

---

## Objeto `usuario` (estructura base)

Este objeto aparece en las respuestas de registro, login y perfil:

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellidoPaterno": "García",
  "apellidoMaterno": "López",
  "correo": "juan@example.com",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur",
  "UsuarioRol": "Amateur"
}
```

> `nivelUsuario` es el valor interno. `UsuarioRol` es el display label — úsalo para mostrar en UI.

---

## Módulo: Usuarios

### Registro

```
POST /api/usuarios/registro/
```

**Body:**
```json
{
  "nombre": "Juan",
  "apellidoPaterno": "García",
  "apellidoMaterno": "López",
  "correo": "juan@example.com",
  "password": "contraseña123",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur"
}
```

**Valores válidos:**
- `sexo`: `"Masculino"` | `"Femenino"` | `"Otro"`
- `nivelUsuario`: `"Amateur"` | `"Semi-Pro"` | `"Profesional"` | `"Entrenador"`

**Respuesta `201`:**
```json
{
  "usuario": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "apellidoMaterno": "López",
    "correo": "juan@example.com",
    "sexo": "Masculino",
    "edad": 25,
    "altura": 180,
    "peso": 75,
    "nivelUsuario": "Amateur",
    "UsuarioRol": "Amateur"
  },
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "mensaje": "Usuario registrado exitosamente"
}
```

---

### Login

```
POST /api/login/
```

**Body:**
```json
{
  "correo": "juan@example.com",
  "password": "contraseña123"
}
```

**Respuesta `200`:**
```json
{
  "usuario": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "apellidoMaterno": "López",
    "correo": "juan@example.com",
    "sexo": "Masculino",
    "edad": 25,
    "altura": 180,
    "peso": 75,
    "nivelUsuario": "Amateur",
    "UsuarioRol": "Amateur"
  },
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "mensaje": "Login exitoso"
}
```

**Error `401`:**
```json
{ "error": "Credenciales inválidas" }
```

**Error `403`:**
```json
{ "error": "El usuario está desactivado" }
```

---

### Renovar token

```
POST /api/token/refresh/
```

**Body:**
```json
{ "refresh": "<refresh_token>" }
```

**Respuesta `200`:**
```json
{ "access": "<nuevo_access_token>" }
```

---

### Perfil del usuario autenticado

```
POST /api/usuarios/perfil/
Authorization: Bearer <token>
```

**Respuesta `200`:**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellidoPaterno": "García",
  "apellidoMaterno": "López",
  "correo": "juan@example.com",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur",
  "UsuarioRol": "Amateur"
}
```

---

### Cambiar contraseña

```
POST /api/usuarios/cambiar_password/
Authorization: Bearer <token>
```

**Body:**
```json
{
  "password_actual": "contraseña123",
  "password_nuevo": "nueva456"
}
```

**Respuesta `200`:**
```json
{ "mensaje": "Contraseña cambiada exitosamente" }
```

**Error `400`:**
```json
{ "error": "La contraseña actual es incorrecta" }
```

---

### Logout

```
POST /api/usuarios/logout/
Authorization: Bearer <token>
```

**Respuesta `200`:**
```json
{ "mensaje": "Logout exitoso" }
```

---

## Módulo: Amistad

### Objeto `friendship` (estructura base)

Este objeto aparece en solicitudes y lista de amigos:

```json
{
  "id": 1,
  "user": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "correo": "juan@example.com",
    "nivelUsuario": "Amateur"
  },
  "friend": {
    "id": 2,
    "nombre": "Pedro",
    "apellidoPaterno": "Rodríguez",
    "correo": "pedro@example.com",
    "nivelUsuario": "Semi-Pro"
  },
  "status": "PENDIENTE",
  "created_at": "2026-05-21T20:00:00Z"
}
```

> `status` posibles valores: `"PENDIENTE"` | `"ACEPTADO"`

---

### Buscar jugadores

```
GET /api/players/search/?term=<texto>
Authorization: Bearer <token>
```

**Query param:** `term` — nombre, apellido o correo (mínimo 1 carácter).

**Respuesta `200`:**
```json
[
  {
    "player_id": 2,
    "correo": "pedro@example.com",
    "display_name": "Pedro Rodríguez Soto",
    "nivel": "Semi-Pro",
    "button_state": "NONE"
  },
  {
    "player_id": 3,
    "correo": "maria@example.com",
    "display_name": "María González Díaz",
    "nivel": "Profesional",
    "button_state": "PENDING"
  }
]
```

**`button_state` posibles valores:**

| Valor | Significado | Acción en UI |
|---|---|---|
| `NONE` | Sin relación | Mostrar botón "Agregar" |
| `PENDING` | Solicitud enviada | Botón deshabilitado "Pendiente" |
| `PARTNERS` | Ya son amigos | Botón deshabilitado "Amigos" |

---

### Enviar solicitud de amistad

```
POST /api/friends/request/
Authorization: Bearer <token>
```

**Body:**
```json
{ "friend_id": 2 }
```

**Respuesta `201`:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "correo": "juan@example.com",
    "nivelUsuario": "Amateur"
  },
  "friend": {
    "id": 2,
    "nombre": "Pedro",
    "apellidoPaterno": "Rodríguez",
    "correo": "pedro@example.com",
    "nivelUsuario": "Semi-Pro"
  },
  "status": "PENDIENTE",
  "created_at": "2026-05-21T20:00:00Z"
}
```

**Errores `400`:**
```json
{ "friend_id": ["Ya existe una relación con este usuario."] }
{ "friend_id": ["Este usuario ya te envió una solicitud."] }
{ "friend_id": ["No puedes enviarte una solicitud a ti mismo."] }
{ "friend_id": ["Usuario no encontrado."] }
```

---

### Ver solicitudes recibidas

```
GET /api/friends/requests/
Authorization: Bearer <token>
```

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "nombre": "Pedro",
      "apellidoPaterno": "Rodríguez",
      "correo": "pedro@example.com",
      "nivelUsuario": "Semi-Pro"
    },
    "friend": {
      "id": 1,
      "nombre": "Juan",
      "apellidoPaterno": "García",
      "correo": "juan@example.com",
      "nivelUsuario": "Amateur"
    },
    "status": "PENDIENTE",
    "created_at": "2026-05-21T20:00:00Z"
  }
]
```

> `user` es quien envió la solicitud. `friend` es el usuario autenticado (tú).

---

### Aceptar solicitud

```
PATCH /api/friends/request/<id>/accept/
Authorization: Bearer <token>
```

> `<id>` es el `id` del objeto `friendship`.

**Respuesta `200`:**
```json
{
  "id": 1,
  "user": {
    "id": 2,
    "nombre": "Pedro",
    "apellidoPaterno": "Rodríguez",
    "correo": "pedro@example.com",
    "nivelUsuario": "Semi-Pro"
  },
  "friend": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "García",
    "correo": "juan@example.com",
    "nivelUsuario": "Amateur"
  },
  "status": "ACEPTADO",
  "created_at": "2026-05-21T20:00:00Z"
}
```

**Error `404`:**
```json
{ "error": "Solicitud no encontrada." }
```

---

### Rechazar solicitud

```
DELETE /api/friends/request/<id>/reject/
Authorization: Bearer <token>
```

**Respuesta `204`:** Sin body.

**Error `404`:**
```json
{ "error": "Solicitud no encontrada." }
```

---

### Listar amigos

```
GET /api/friends/
Authorization: Bearer <token>
```

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "nombre": "Juan",
      "apellidoPaterno": "García",
      "correo": "juan@example.com",
      "nivelUsuario": "Amateur"
    },
    "friend": {
      "id": 2,
      "nombre": "Pedro",
      "apellidoPaterno": "Rodríguez",
      "correo": "pedro@example.com",
      "nivelUsuario": "Semi-Pro"
    },
    "status": "ACEPTADO",
    "created_at": "2026-05-21T20:00:00Z"
  }
]
```

---

### Eliminar amigo

```
DELETE /api/friends/<id>/
Authorization: Bearer <token>
```

> `<id>` es el `id` del objeto `friendship`, no el `id` del usuario.

**Respuesta `204`:** Sin body.

**Error `404`:**
```json
{ "error": "Amistad no encontrada." }
```

---

## Notas generales

- Todos los timestamps vienen en formato **ISO 8601 UTC**.
- El token `access` debe guardarse en memoria (no en `localStorage` por seguridad).
- Si una respuesta devuelve `401`, el token expiró — usar `/api/token/refresh/` para renovarlo.
- El `id` del objeto `friendship` y el `id` del usuario son distintos — no confundirlos al construir las llamadas de aceptar/rechazar/eliminar.
- El buscador excluye al usuario autenticado de los resultados automáticamente.
- La lista de amigos (`GET /api/friends/`) solo muestra relaciones donde `user` eres tú — no apareces duplicado.
