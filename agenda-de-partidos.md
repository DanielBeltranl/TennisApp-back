# TennisApp — Referencia de API para Frontend

Base URL: `http://localhost:8000/api`

Todos los endpoints protegidos requieren el header:
```
Authorization: Bearer <access_token>
```

---

## Índice

1. [Autenticación](#1-autenticación)
2. [Usuarios](#2-usuarios)
3. [Sistema de Amigos](#3-sistema-de-amigos)
4. [Partidos](#4-partidos)

---

## 1. Autenticación

### 1.1 Login

```
POST /api/login/
```

No requiere autenticación.

**Body:**
```json
{
  "correo": "usuario@mail.com",
  "password": "contraseña123"
}
```

**Respuesta 200:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

**Errores:**
- `401` — credenciales incorrectas

---

### 1.2 Refresh token

```
POST /api/token/refresh/
```

No requiere autenticación.

**Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```

**Respuesta 200:**
```json
{
  "access": "<nuevo_jwt_access_token>"
}
```

**Errores:**
- `401` — refresh token inválido o expirado

---

### 1.3 Verificar token

```
POST /api/token/verify/
```

**Body:**
```json
{
  "token": "<jwt_access_token>"
}
```

**Respuesta 200:** `{}` (objeto vacío — el token es válido)

**Errores:**
- `401` — token inválido o expirado

---

### 1.4 Logout

```
POST /api/usuarios/logout/
```

Requiere autenticación. Invalida el token activo y lo elimina de sesiones.

**Body:** ninguno

**Respuesta 200:**
```json
{
  "mensaje": "Logout exitoso"
}
```

**Errores:**
- `404` — sesión no encontrada o ya fue cerrada

---

### 1.5 Sesiones activas

```
GET /api/usuarios/sesiones_activas/
```

Requiere autenticación.

**Respuesta 200:**
```json
{
  "sesiones": [
    {
      "id": 1,
      "created_at": "2026-05-21T10:00:00Z",
      "expires_at": "2026-05-21T11:00:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total": 1
}
```

---

## 2. Usuarios

### 2.1 Registro

```
POST /api/usuarios/registro/
```

No requiere autenticación.

**Body:**
```json
{
  "nombre": "Juan",
  "apellidoPaterno": "Pérez",
  "apellidoMaterno": "García",
  "correo": "juan@mail.com",
  "password": "contraseña123",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur"
}
```

**Campos y valores válidos:**

| Campo | Tipo | Valores válidos |
|---|---|---|
| `sexo` | string | `"Masculino"`, `"Femenino"`, `"Otro"` |
| `nivelUsuario` | string | `"Amateur"`, `"Semi-Pro"`, `"Profesional"`, `"Entrenador"` |
| `edad` | int | — |
| `altura` | int | en centímetros |
| `peso` | int | en kilogramos |

**Respuesta 201:**
```json
{
  "usuario": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "Pérez",
    "apellidoMaterno": "García",
    "correo": "juan@mail.com",
    "sexo": "Masculino",
    "edad": 25,
    "altura": 180,
    "peso": 75,
    "nivelUsuario": "Amateur",
    "UsuarioRol": "Amateur"
  },
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "mensaje": "Usuario registrado exitosamente"
}
```

> El registro devuelve tokens directamente — no es necesario hacer login después.

**Errores:**
- `400` — campos faltantes o correo ya registrado

---

### 2.2 Perfil del usuario autenticado

```
POST /api/usuarios/perfil/
```

Requiere autenticación. No requiere body.

**Respuesta 200:**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellidoPaterno": "Pérez",
  "apellidoMaterno": "García",
  "correo": "juan@mail.com",
  "sexo": "Masculino",
  "edad": 25,
  "altura": 180,
  "peso": 75,
  "nivelUsuario": "Amateur",
  "UsuarioRol": "Amateur"
}
```

---

### 2.3 Cambiar contraseña

```
POST /api/usuarios/cambiar_password/
```

Requiere autenticación.

**Body:**
```json
{
  "password_actual": "contraseña_vieja",
  "password_nuevo": "contraseña_nueva"
}
```

**Respuesta 200:**
```json
{
  "mensaje": "Contraseña cambiada exitosamente"
}
```

**Errores:**
- `400` — contraseña actual incorrecta o campos faltantes

---

## 3. Sistema de Amigos

### 3.1 Buscar jugadores

```
GET /api/players/search/?term=<texto>
```

Requiere autenticación. Busca por nombre, apellido o correo (coincidencia parcial).

**Query param:** `term` — mínimo 1 carácter

**Respuesta 200:**
```json
[
  {
    "player_id": 2,
    "correo": "carlos@mail.com",
    "display_name": "Carlos López Soto",
    "nivel": "Semi-Pro",
    "button_state": "NONE"
  }
]
```

**Valores de `button_state`:**

| Valor | Significado | Acción sugerida en UI |
|---|---|---|
| `"NONE"` | Sin relación previa | Mostrar botón "Agregar" |
| `"PENDING"` | Solicitud enviada por ti | Mostrar "Pendiente" (deshabilitado) |
| `"PARTNERS"` | Ya son amigos | Mostrar "Amigos" (deshabilitado) |

> El usuario autenticado nunca aparece en los resultados.

---

### 3.2 Enviar solicitud de amistad

```
POST /api/friends/request/
```

Requiere autenticación.

**Body:**
```json
{
  "friend_id": 2
}
```

**Respuesta 201:**
```json
{
  "id": 10,
  "user": 1,
  "friend": 2,
  "status": "PENDIENTE",
  "created_at": "2026-05-21T10:00:00Z"
}
```

**Errores:**
- `400` — solicitud ya existente, o intentás agregarte a vos mismo

---

### 3.3 Ver solicitudes recibidas (pendientes)

```
GET /api/friends/requests/
```

Requiere autenticación. Devuelve solicitudes que **otros te enviaron a vos**.

**Respuesta 200:**
```json
[
  {
    "id": 10,
    "user": 1,
    "friend": 2,
    "status": "PENDIENTE",
    "created_at": "2026-05-21T10:00:00Z"
  }
]
```

> Usar el campo `id` de cada solicitud para aceptar o rechazar.

---

### 3.4 Aceptar solicitud de amistad

```
PATCH /api/friends/request/<id>/accept/
```

Requiere autenticación. Solo puede aceptar el usuario que **recibió** la solicitud.

**Body:** ninguno

**Respuesta 200:**
```json
{
  "id": 10,
  "user": 1,
  "friend": 2,
  "status": "ACEPTADO",
  "created_at": "2026-05-21T10:00:00Z"
}
```

**Errores:**
- `404` — solicitud no encontrada o ya fue procesada

---

### 3.5 Rechazar solicitud de amistad

```
DELETE /api/friends/request/<id>/reject/
```

Requiere autenticación. Solo puede rechazar el usuario que **recibió** la solicitud.

**Respuesta 204:** sin body

**Errores:**
- `404` — solicitud no encontrada

---

### 3.6 Lista de amigos

```
GET /api/friends/
```

Requiere autenticación. Devuelve todos los amigos confirmados del usuario autenticado.

**Respuesta 200:**
```json
[
  {
    "id": 10,
    "user": 1,
    "friend": 2,
    "status": "ACEPTADO",
    "created_at": "2026-05-21T10:00:00Z"
  }
]
```

---

### 3.7 Eliminar amigo

```
DELETE /api/friends/<id>/
```

Requiere autenticación. El `<id>` es el `id` del registro de amistad (obtenido en la lista de amigos). Elimina la relación en ambas direcciones.

**Respuesta 204:** sin body

**Errores:**
- `404` — amistad no encontrada

---

## 4. Partidos

### 4.1 Agendar partido

```
POST /api/matches/schedule/
```

Requiere autenticación. El usuario autenticado es el creador; el partido nace en estado `PENDIENTE`.

**Body:**
```json
{
  "id_player_invited": 2,
  "location": "Club de Tenis Santiago",
  "surface": "Clay",
  "best_of": 3
}
```

**Campos y valores válidos:**

| Campo | Tipo | Valores válidos |
|---|---|---|
| `id_player_invited` | int | ID del jugador invitado |
| `location` | string | Texto libre |
| `surface` | string | `"Clay"`, `"Hard"`, `"Grass"` |
| `best_of` | int | `1`, `3`, `5` |

**Respuesta 201:**
```json
{
  "id_match": "550e8400-e29b-41d4-a716-446655440000",
  "creator": {
    "id": 1,
    "nombre": "Juan",
    "apellidoPaterno": "Pérez",
    "correo": "juan@mail.com"
  },
  "invited": {
    "id": 2,
    "nombre": "Carlos",
    "apellidoPaterno": "López",
    "correo": "carlos@mail.com"
  },
  "location": "Club de Tenis Santiago",
  "surface": "Clay",
  "best_of": 3,
  "match_state": "PENDIENTE",
  "created_at": "2026-05-21T10:00:00Z"
}
```

**Errores:**
- `400` — el invitado no es amigo del creador
- `400` — el creador se invitó a sí mismo
- `400` — campos faltantes o inválidos

---

### 4.2 Estados del partido

El campo `match_state` sigue este flujo:

```
PENDIENTE → ACEPTADO → INICIADO → PAUSADO → FINALIZADA
```

| Estado | Significado |
|---|---|
| `PENDIENTE` | Partido agendado, esperando que el invitado acepte |
| `ACEPTADO` | El invitado aceptó, listo para iniciar |
| `INICIADO` | Partido en curso |
| `PAUSADO` | Partido pausado |
| `FINALIZADA` | Partido terminado |

> Los endpoints de transición de estado (aceptar invitación, iniciar partido, etc.) están pendientes de implementación.

---

## Notas generales

- Todos los IDs de partido son **UUID**.
- Todos los IDs de usuario son **enteros**.
- Las fechas están en formato **ISO 8601 UTC** (`"2026-05-21T10:00:00Z"`).
- El módulo de **notificaciones** está pendiente de implementación — cuando esté disponible, agendar un partido disparará una notificación al jugador invitado.
