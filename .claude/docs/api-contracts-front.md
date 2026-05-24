# Contratos API — TennisApp Backend
> Documento generado post-implementación Fase 1. Refleja el estado actual de la API y los cambios que impactan al frontend.

---
## Descripcion

- Estas son una serie de correcciones que se hicieron pensando en el correcto funcionamiento de la app, asi que no reconstruyas, refactoriza sobre lo que ya esta.

## Índice

1. [Contexto del cambio](#1-contexto-del-cambio)
2. [JWT — nueva estructura](#2-jwt--nueva-estructura)
3. [Auth — endpoints modificados](#3-auth--endpoints-modificados)
4. [Matches — endpoints modificados](#4-matches--endpoints-modificados)
5. [Coaching — endpoints próximos (Fase 3)](#5-coaching--endpoints-próximos-fase-3)
6. [Sin cambios](#6-sin-cambios)

---

## 1. Contexto del cambio

Se separó el concepto de **rol** del concepto de **nivel de juego**:

| Antes | Después |
|-------|---------|
| `nivelUsuario` contenía `Entrenador`, `Amateur`, `Semi-Pro`, `Profesional` | `rol` = `Jugador` \| `Entrenador` |
| Un solo tipo de usuario | `nivelUsuario` = `Amateur` \| `Semi-Pro` \| `Profesional` \| `null` (solo para jugadores) |
| `edad` (número entero) | `fecha_nacimiento` (string `YYYY-MM-DD`) |
| `id_player_invited` siempre requerido en partidos | `id_player_invited` opcional — admite invitados sin cuenta |

**Implicancias para el front:**
- El JWT tiene un campo nuevo `rol` que determina qué dashboard mostrar.
- El formulario de registro ahora bifurca según `rol`.
- El nivel del jugador llega como `null` hasta que un entrenador lo asigne (Fase 3).

---

## 2. JWT — nueva estructura

Todos los endpoints autenticados leen el token. Esta es la nueva estructura del payload:

```json
{
  "user_id": 1,
  "correo": "jugador@mail.com",
  "nombre": "Nombre",
  "rol": "Jugador",
  "nivelUsuario": "Amateur",
  "sexo": "Masculino",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Variantes por rol

**Jugador recién registrado (sin entrenador asignado)**
```json
{
  "rol": "Jugador",
  "nivelUsuario": null,
  "sexo": "Masculino"
}
```
> El front debe manejar `nivelUsuario: null` mostrando un mensaje del tipo *"Tu entrenador aún no te ha asignado un nivel"*.

**Entrenador**
```json
{
  "rol": "Entrenador",
  "nivelUsuario": null,
  "sexo": null
}
```

### Valores posibles

| Campo | Valores |
|-------|---------|
| `rol` | `"Jugador"` \| `"Entrenador"` |
| `nivelUsuario` | `"Amateur"` \| `"Semi-Pro"` \| `"Profesional"` \| `null` |
| `sexo` | `"Masculino"` \| `"Femenino"` \| `"Otro"` \| `null` |

---

## 3. Auth — endpoints modificados

### `POST /api/login/`
> Sin cambios en request. El response (JWT) ahora incluye `rol`.

**Request** — sin cambios
```json
{
  "correo": "usuario@mail.com",
  "password": "contraseña123"
}
```

**Response** — JWT con nuevo campo `rol`
```json
{
  "access": "<jwt_token>",
  "refresh": "<jwt_token>"
}
```

---

### `POST /api/usuarios/registro/`
> **BREAKING CHANGE**: `edad` eliminado, `rol` y `fecha_nacimiento` son nuevos campos.

#### Registro de JUGADOR

**Request**
```json
{
  "nombre": "Carlos",
  "apellidoPaterno": "González",
  "apellidoMaterno": "Pérez",
  "correo": "carlos@mail.com",
  "password": "segura123",
  "rol": "Jugador",
  "sexo": "Masculino",
  "fecha_nacimiento": "1995-08-14",
  "altura": 180,
  "peso": 78
}
```
> `nivelUsuario` **NO se envía en el registro**. Lo asigna el entrenador después.

**Response `201`**
```json
{
  "usuario": {
    "id": 5,
    "nombre": "Carlos",
    "apellidoPaterno": "González",
    "apellidoMaterno": "Pérez",
    "correo": "carlos@mail.com",
    "rol": "Jugador",
    "sexo": "Masculino",
    "fecha_nacimiento": "1995-08-14",
    "altura": 180,
    "peso": 78,
    "nivelUsuario": null
  },
  "access": "<jwt_token>",
  "refresh": "<jwt_token>",
  "mensaje": "Usuario registrado exitosamente"
}
```

#### Registro de ENTRENADOR

**Request**
```json
{
  "nombre": "Martín",
  "apellidoPaterno": "López",
  "apellidoMaterno": "Silva",
  "correo": "martin@mail.com",
  "password": "segura123",
  "rol": "Entrenador",
  "fecha_nacimiento": "1980-03-22"
}
```
> Entrenadores **no envían** `sexo`, `altura`, ni `peso`.

**Response `201`**
```json
{
  "usuario": {
    "id": 6,
    "nombre": "Martín",
    "apellidoPaterno": "López",
    "apellidoMaterno": "Silva",
    "correo": "martin@mail.com",
    "rol": "Entrenador",
    "sexo": null,
    "fecha_nacimiento": "1980-03-22",
    "altura": null,
    "peso": null,
    "nivelUsuario": null
  },
  "access": "<jwt_token>",
  "refresh": "<jwt_token>",
  "mensaje": "Usuario registrado exitosamente"
}
```

> **Nota:** La validación diferenciada por rol (campos obligatorios según `rol`) se implementa en Fase 2. Por ahora el backend acepta ambas variantes con los campos opcionales en null.

---

## 4. Matches — endpoints modificados

### `POST /api/matches/schedule/`
> Se agrega soporte para **invitados sin cuenta**. Próximamente en Fase 4 — por ahora `id_player_invited` sigue siendo obligatorio.

**Request actual (sin cambios)**
```json
{
  "id_player_invited": 3,
  "location": "Club Santa Lucía",
  "surface": "Clay",
  "best_of": 3
}
```

**Request futuro (Fase 4) — invitado sin cuenta**
```json
{
  "guest_name": "Pedro Soto",
  "location": "Club Santa Lucía",
  "surface": "Clay",
  "best_of": 3
}
```
> Se envía `guest_name` **O** `id_player_invited`, nunca ambos.

**Response** — agrega campo `guest_name`
```json
{
  "id_match": "uuid",
  "creator": {
    "id": 1,
    "nombre": "Carlos",
    "apellidoPaterno": "González",
    "correo": "carlos@mail.com"
  },
  "invited": null,
  "id_player_invited": null,
  "guest_name": "Pedro Soto",
  "location": "Club Santa Lucía",
  "surface": "Clay",
  "best_of": 3,
  "match_state": "PENDIENTE",
  "created_at": "2026-05-23T14:00:00Z"
}
```

### Otros endpoints de matches — sin cambios en contrato

Los demás endpoints de partidos (`/accept/`, `/start/`, `/point/`, etc.) no cambian su contrato de request/response. Solo se ven afectados internamente por el `id_player_invited` nullable cuando se juega con invitado (Fase 4).

---

## 5. Coaching — endpoints próximos (Fase 3)

Estos endpoints **aún no están disponibles**. Se documentan acá para que el front pueda preparar las pantallas.

---

### `GET /api/coaching/entrenadores/?q=nombre`
> Busca entrenadores por nombre parcial.

**Response `200`**
```json
[
  {
    "id": 6,
    "nombre": "Martín",
    "apellidoPaterno": "López",
    "correo": "martin@mail.com"
  }
]
```

---

### `POST /api/coaching/solicitudes/`
> Jugador envía solicitud de asociación a un entrenador.

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
  "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "correo": "carlos@mail.com" },
  "entrenador": { "id": 6, "nombre": "Martín", "apellidoPaterno": "López", "correo": "martin@mail.com" },
  "status": "PENDIENTE",
  "created_at": "2026-05-23T14:00:00Z"
}
```

---

### `GET /api/coaching/solicitudes/recibidas/`
> Entrenador consulta sus solicitudes pendientes.

**Response `200`**
```json
[
  {
    "id": 1,
    "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "correo": "carlos@mail.com" },
    "status": "PENDIENTE",
    "created_at": "2026-05-23T14:00:00Z"
  }
]
```

---

### `PATCH /api/coaching/solicitudes/{id}/aceptar/`
> Entrenador acepta la solicitud y asigna el nivel al jugador. Dispara el modal de selección de nivel en el front.

**Request**
```json
{
  "nivel": "Amateur"
}
```

**Response `200`**
```json
{
  "id": 1,
  "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "correo": "carlos@mail.com" },
  "status": "ACEPTADA",
  "nivel_asignado": "Amateur"
}
```
> `nivel` acepta: `"Amateur"` | `"Semi-Pro"` | `"Profesional"`

---

### `PATCH /api/coaching/solicitudes/{id}/rechazar/`
> Sin body. Rechaza la solicitud.

**Response `200`**
```json
{
  "id": 1,
  "status": "RECHAZADA"
}
```

---

### `GET /api/matches/dashboard-entrenador/`
> Historial de partidos de todos los jugadores del entrenador, ordenados por fecha.

**Response `200`**
```json
{
  "partidos": [
    {
      "id_match": "uuid",
      "jugador": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González" },
      "creator": { "id": 5, "nombre": "Carlos", "apellidoPaterno": "González", "correo": "carlos@mail.com" },
      "invited": { "id": 3, "nombre": "Juan", "apellidoPaterno": "Martínez", "correo": "juan@mail.com" },
      "location": "Club Santa Lucía",
      "surface": "Clay",
      "match_state": "FINALIZADA",
      "created_at": "2026-05-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 6. Sin cambios

Los siguientes endpoints **no cambian** su contrato de request/response:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `POST /api/token/refresh/` | POST | Refresh token |
| `POST /api/token/verify/` | POST | Verificar token |
| `POST /api/usuarios/perfil/` | POST | Ver perfil propio |
| `POST /api/usuarios/cambiar_password/` | POST | Cambiar contraseña |
| `POST /api/usuarios/logout/` | POST | Cerrar sesión |
| `GET /api/players/search/?term=` | GET | Buscar jugadores (amigos) |
| `POST /api/friends/request/` | POST | Enviar solicitud de amistad |
| `GET /api/friends/requests/` | GET | Ver solicitudes pendientes |
| `PATCH /api/friends/request/{id}/accept/` | PATCH | Aceptar solicitud |
| `DELETE /api/friends/request/{id}/reject/` | DELETE | Rechazar solicitud |
| `GET /api/friends/` | GET | Lista de amigos |
| `DELETE /api/friends/{id}/` | DELETE | Eliminar amigo |
| `PATCH /api/matches/{id}/accept/` | PATCH | Aceptar partido |
| `DELETE /api/matches/{id}/reject/` | DELETE | Rechazar partido |
| `PATCH /api/matches/{id}/start/` | PATCH | Iniciar partido |
| `PATCH /api/matches/{id}/pause/` | PATCH | Pausar partido |
| `PATCH /api/matches/{id}/resume/` | PATCH | Reanudar partido |
| `PATCH /api/matches/{id}/finish/` | PATCH | Finalizar partido |
| `GET /api/matches/{id}/recovery/` | GET | Recuperar estado partido |
| `POST /api/matches/{id}/point/` | POST | Registrar punto |
| `DELETE /api/matches/{id}/point/undo/` | DELETE | Deshacer punto |
| `GET /api/matches/my-created/` | GET | Mis partidos creados |
| `GET /api/matches/my-invited/` | GET | Mis partidos invitado |
| `GET /api/statistics/match/{id}/` | GET | Stats de un partido |
| `GET /api/statistics/global/` | GET | Stats globales |

---

## Resumen de breaking changes

| Campo | Antes | Después | Afecta |
|-------|-------|---------|--------|
| `nivelUsuario` | `"Entrenador"` era valor válido | Ya no existe — usar `rol` | Login, Registro, JWT |
| `edad` | `integer` requerido | **Eliminado** | Registro |
| `fecha_nacimiento` | No existía | `"YYYY-MM-DD"` requerido | Registro |
| `rol` | No existía | `"Jugador"` \| `"Entrenador"` requerido | Registro, JWT |
| `sexo`, `altura`, `peso` | Requeridos para todos | Opcionales (null para entrenadores) | Registro |
| `guest_name` | No existía | Campo nuevo en `MatchData` (Fase 4) | Schedule match |
