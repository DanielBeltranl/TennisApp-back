# API Endpoints — TennisApp Backend

> Base URL: `http://localhost:8000`
> Auth: todas las rutas protegidas requieren header `Authorization: Bearer <access_token>`
> Última actualización: 2026-05-25

---

## Índice

- [Autenticación](#autenticación)
- [Usuarios](#usuarios)
- [Partidos — Matches](#partidos--matches)
- [Estadísticas](#estadísticas)
- [Amistades — Friendship](#amistades--friendship)
- [Coaching](#coaching)

---

## Autenticación

### `POST /api/login/`
**Auth:** Ninguna

**Body:**
```json
{
  "correo": "usuario@mail.com",
  "password": "secreto"
}
```

**Respuesta 200:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```
> El token incluye claims: `correo`, `nombre`, `rol`, `nivelUsuario`, `sexo`.

---

### `POST /api/token/refresh/`
**Auth:** Ninguna

**Body:**
```json
{ "refresh": "<jwt_refresh_token>" }
```

**Respuesta 200:**
```json
{ "access": "<nuevo_access_token>" }
```

---

### `POST /api/token/verify/`
**Auth:** Ninguna

**Body:**
```json
{ "token": "<jwt_token>" }
```

**Respuesta 200:** `{}` (vacío si válido, 401 si inválido)

---

## Usuarios

### `POST /api/usuarios/registro/`
**Auth:** Ninguna

**Body jugador:**
```json
{
  "rol": "Jugador",
  "nombre": "string",
  "apellidoPaterno": "string",
  "apellidoMaterno": "string",
  "correo": "email",
  "password": "string",
  "sexo": "Masculino | Femenino | Otro",
  "fecha_nacimiento": "YYYY-MM-DD",
  "altura": 175,
  "peso": 70
}
```

**Body entrenador:**
```json
{
  "rol": "Entrenador",
  "nombre": "string",
  "apellidoPaterno": "string",
  "apellidoMaterno": "string",
  "correo": "email",
  "password": "string",
  "fecha_nacimiento": "YYYY-MM-DD"
}
```

**Respuesta 201:**
```json
{
  "usuario": {
    "id": 1,
    "nombre": "string",
    "apellidoPaterno": "string",
    "apellidoMaterno": "string",
    "correo": "email",
    "rol": "Jugador | Entrenador",
    "sexo": "string | null",
    "fecha_nacimiento": "YYYY-MM-DD | null",
    "altura": 175,
    "peso": 70,
    "nivelUsuario": "Amateur | Semi-Pro | Profesional | null"
  },
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "mensaje": "Usuario registrado exitosamente"
}
```

---

### `POST /api/usuarios/perfil/`
**Auth:** Requerida (cualquier rol)
**Body:** Ninguno

**Respuesta 200:**
```json
{
  "id": 1,
  "nombre": "string",
  "apellidoPaterno": "string",
  "apellidoMaterno": "string",
  "correo": "email",
  "rol": "Jugador | Entrenador",
  "sexo": "string | null",
  "fecha_nacimiento": "YYYY-MM-DD | null",
  "altura": 175,
  "peso": 70,
  "nivelUsuario": "Amateur | Semi-Pro | Profesional | null"
}
```

---

### `POST /api/usuarios/cambiar_password/`
**Auth:** Requerida (cualquier rol)

**Body:**
```json
{
  "password_actual": "string",
  "password_nuevo": "string"
}
```

**Respuesta 200:**
```json
{ "mensaje": "Contraseña cambiada exitosamente" }
```

---

### `POST /api/usuarios/logout/`
**Auth:** Requerida (cualquier rol)
**Body:** Ninguno

**Respuesta 200:**
```json
{ "mensaje": "Logout exitoso" }
```

---

### `GET /api/usuarios/sesiones_activas/`
**Auth:** Requerida (cualquier rol)

**Respuesta 200:**
```json
{
  "sesiones": [
    {
      "id": 1,
      "created_at": "datetime",
      "expires_at": "datetime",
      "ip_address": "string",
      "user_agent": "string"
    }
  ],
  "total": 1
}
```

---

## Partidos — Matches

### Objeto base `MatchData`
```json
{
  "id_match": "uuid",
  "entrenador": { "id", "nombre", "apellidoPaterno", "correo" },
  "local_player": { "id", "nombre", "apellidoPaterno", "correo" },
  "invited": { "id", "nombre", "apellidoPaterno", "correo" },
  "guest_name": "string | null",
  "location": "string",
  "surface": "Clay | Hard",
  "best_of": 1,
  "match_state": "PENDIENTE | ACEPTADO | INICIADO | PAUSADO | FINALIZADA",
  "scheduled_at": "datetime",
  "score": { ... },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

### `GET /api/matches/schedule/`
**Auth:** `ENTRENADOR`

Retorna los partidos agendados **creados por** el entrenador autenticado, en estado `PENDIENTE` o `ACEPTADO`, ordenados por `scheduled_at` ascendente.

**Respuesta 200:** Array de objetos `ScheduleMatch`:
```json
[
  {
    "id_match": "uuid",
    "entrenador": { "id", "nombre", "apellidoPaterno", "correo" },
    "local_player": { "id", "nombre", "apellidoPaterno", "correo" },
    "invited": { "id", "nombre", "apellidoPaterno", "correo" },
    "scheduled_at": "datetime",
    "guest_name": "string | null",
    "location": "string",
    "surface": "Clay | Hard",
    "best_of": 1,
    "match_state": "PENDIENTE | ACEPTADO",
    "created_at": "datetime"
  }
]
```

---

### `POST /api/matches/schedule/`
**Auth:** `ENTRENADOR`

Agenda un partido. El jugador local debe ser uno de los entrenados del entrenador.
Enviar `id_invited_player` (jugador registrado) **o** `guest_name` (externo), nunca ambos.
- Si tiene `id_invited_player` → nace en `PENDIENTE` (espera aceptación)
- Si tiene `guest_name` → nace en `ACEPTADO` directamente

**Body:**
```json
{
  "id_local_player": 5,
  "id_invited_player": 8,
  "guest_name": null,
  "scheduled_at": "2026-06-01T18:00:00Z",
  "location": "Club Providencia",
  "surface": "Clay | Hard",
  "best_of": 1
}
```

**Respuesta 201:**
```json
{ "message": "Partido agendado correctamente.", "error": null }
```

---

### `GET /api/matches/coach/players-invitations/`
**Auth:** `ENTRENADOR`

Retorna todos los partidos en estado `PENDIENTE` donde el `id_invited_player` es uno de los jugadores asignados al entrenador, pero que el entrenador **no** creó.

**Respuesta 200:** Array de objetos `ScheduleMatch` (mismo shape que `GET /schedule/`)

---

### `GET /api/matches/my-created/`
**Auth:** Cualquier usuario autenticado

Retorna todos los partidos donde el usuario autenticado es `local_player`, ordenados por `created_at` descendente.

**Respuesta 200:** Array de `MatchData` completo (con `score` anidado).

---

### `GET /api/matches/my-invited/`
**Auth:** Cualquier usuario autenticado

Retorna todos los partidos donde el usuario autenticado es `id_invited_player`, ordenados por `created_at` descendente.

**Respuesta 200:** Array de `MatchData` completo (con `score` anidado).

---

### `GET /api/matches/summary/`
**Auth:** Cualquier usuario autenticado

Retorna los últimos 5 partidos **finalizados** donde el usuario participó (local o invitado).

**Respuesta 200:**
```json
[
  {
    "id_match": "uuid",
    "entrenador": { ... },
    "local_player": { ... },
    "invited": { ... },
    "guest_name": "string | null",
    "location": "string",
    "surface": "string",
    "best_of": 1,
    "match_state": "FINALIZADA",
    "winner": { "id", "nombre", "apellidoPaterno", "correo" },
    "duration": 3600,
    "sets": [
      {
        "score_p1": 6,
        "score_p2": 4,
        "games": [
          { "p1_game_final_score": 1, "p2_game_final_score": 0 }
        ]
      }
    ],
    "scheduled_at": "datetime",
    "created_at": "datetime"
  }
]
```

---

### `PATCH /api/matches/{uuid}/accept/`
**Auth:** Usuario autenticado (debe ser el `id_invited_player`)

Acepta la invitación a un partido en estado `PENDIENTE`. Solo el jugador invitado puede aceptar.

**Body:** Ninguno

**Respuesta 200:** `MatchData` completo.

---

### `DELETE /api/matches/{uuid}/reject/`
**Auth:** Usuario autenticado (debe ser el `id_invited_player`)

Rechaza y elimina un partido en estado `PENDIENTE`. Solo el jugador invitado puede rechazar.

**Body:** Ninguno

**Respuesta 204:** Sin contenido.

---

### `PATCH /api/matches/{uuid}/start/`
**Auth:** Usuario autenticado (debe ser participante del partido)

Inicia un partido en estado `ACEPTADO`. Crea el `MatchScore`, primer `MatchSet` y primer `MatchGame`.

**Body:**
```json
{ "first_server_id": 5 }
```

**Respuesta 200:** `MatchData` completo.

---

### `PATCH /api/matches/{uuid}/pause/`
**Auth:** Usuario autenticado (debe ser participante)

Pausa un partido en estado `INICIADO`.

**Body:** Ninguno

**Respuesta 200:** `MatchData` completo.

---

### `PATCH /api/matches/{uuid}/resume/`
**Auth:** Usuario autenticado (debe ser participante)

Reanuda un partido en estado `PAUSADO`.

**Body:** Ninguno

**Respuesta 200:** `MatchData` completo.

---

### `PATCH /api/matches/{uuid}/finish/`
**Auth:** Usuario autenticado (debe ser participante)

Finaliza un partido en estado `INICIADO`. Registra el ganador y la duración total.

**Body (partido con invitado):**
```json
{ "winner_id": 5 }
```

**Body (partido con guest — invitado externo):**
```json
{ "winner_id": 5 }
```
> En partidos con `guest_name`, si el local gana se envía su id; si el externo gana, se envía `null` o se omite.

**Respuesta 200:** `MatchData` completo.

---

### `GET /api/matches/{uuid}/recovery/`
**Auth:** Usuario autenticado (debe ser participante)

Recupera el estado completo de un partido en curso (`INICIADO` o `PAUSADO`). Útil para reconectar a una sesión activa.

**Respuesta 200:**
```json
{
  "match": { ... },
  "sets_p1": 1,
  "sets_p2": 0,
  "sets": [
    { "id_set": 1, "set_number": 1, "score_p1": 6, "score_p2": 4, "winner_id": 5 }
  ],
  "current_set": { "id_set": 2, "set_number": 2, "score_p1": 3, "score_p2": 2 },
  "current_game": {
    "id_game": 15,
    "game_number": 6,
    "is_serving": { "id", "nombre", "apellidoPaterno", "correo" }
  },
  "current_score": { "score_p1": "30", "score_p2": "15" },
  "last_point": {
    "id_point": 88,
    "score_p1": "30",
    "score_p2": "15",
    "winner_id": 5,
    "duration": 12,
    "created_at": "datetime"
  }
}
```

---

### `POST /api/matches/{uuid}/point/`
**Auth:** Usuario autenticado (debe ser participante)

Registra un punto en el partido activo. Maneja automáticamente: cierre de game, deuce, ventaja, cierre de set, tiebreak, cierre de partido.

**Body:**
```json
{
  "winner_id": 5,
  "duration": 18
}
```
> En partidos con `guest_name`: si gana el local → `winner_id = id_local_player`; si gana el externo → `winner_id = null` o se omite.

**Respuesta 201:**
```json
{
  "game_closed": false,
  "set_closed": false,
  "match_closed": false,
  "tiebreak_required": false,
  "point": { ... },
  "current_score": { "score_p1": "30", "score_p2": "15" },
  "current_game": { "id_game": 15, "is_serving_id": 5 },
  "current_set": { "score_p1": 3, "score_p2": 2 }
}
```
> Cuando `match_closed: true` también retorna `"winner": { "id", "nombre", ... }`.

---

### `DELETE /api/matches/{uuid}/point/undo/`
**Auth:** Usuario autenticado (debe ser participante)

Deshace el último punto registrado. Si ese punto cerraba un game/set/partido, revierte todos los estados en cascada.

**Body:** Ninguno

**Respuesta 200:**
```json
{ "mensaje": "Punto deshecho." }
```

---

### `GET /api/matches/match-data/{uuid}/`
**Auth:** Cualquier usuario autenticado

Retorna un `MatchData` completo con el marcador anidado.

**Respuesta 200:**
```json
{
  "id_match": "uuid",
  "entrenador": { ... },
  "local_player": { ... },
  "invited": { ... },
  "guest_name": "string | null",
  "location": "string",
  "surface": "string",
  "best_of": 1,
  "match_state": "string",
  "scheduled_at": "datetime",
  "score": {
    "id_match_score": 1,
    "id_partido": "uuid",
    "winner": { ... },
    "duration": 3600,
    "sets": [
      {
        "id_set": 1,
        "score_p1": 6,
        "score_p2": 4,
        "winner": { ... },
        "duration": 2400,
        "created_at": "datetime",
        "games": [
          {
            "id_game": 1,
            "p1_game_final_score": 1,
            "p2_game_final_score": 0,
            "duration": 120,
            "winner": { ... },
            "is_break": false,
            "is_serving": 5,
            "created_at": "datetime"
          }
        ]
      }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
> `score` es `null` si el partido no fue iniciado aún.

---

## Estadísticas

### `GET /api/statistics/match/{uuid}/`
**Auth:** Jugador autenticado (debe ser participante del partido)

Retorna estadísticas completas de un partido **finalizado**. El nivel y sexo se extraen del JWT.

**Respuesta 200:** Objeto con todas las métricas calculadas (puntos por tiempo, distancia, cuartiles, duración media, break points, etc.)

---

### `GET /api/statistics/global/`
**Auth:** Cualquier usuario autenticado

Retorna estadísticas acumuladas de los últimos 14 partidos finalizados del usuario.

**Respuesta 200:** Objeto con métricas históricas agregadas.

---

## Amistades — Friendship

### `GET /api/players/search/?term=<string>`
**Auth:** Requerida (cualquier rol)

Busca jugadores por nombre, apellido o correo. Incluye el estado de relación con el buscador.

**Query param:** `term` (mínimo 1 caracter)

**Respuesta 200:**
```json
[
  {
    "player_id": 5,
    "correo": "jugador@mail.com",
    "display_name": "Juan Pérez García",
    "nivel": "Amateur | null",
    "rol": "Jugador | Entrenador",
    "button_state": "NONE | PENDING | PARTNERS"
  }
]
```

---

### `GET /api/friends/`
**Auth:** Requerida (cualquier rol)

Retorna todos los amigos aceptados del usuario autenticado.

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "user": { "id", "nombre", "apellidoPaterno", "correo", "nivelUsuario" },
    "friend": { "id", "nombre", "apellidoPaterno", "correo", "nivelUsuario" },
    "status": "ACEPTADO",
    "created_at": "datetime"
  }
]
```

---

### `POST /api/friends/request/`
**Auth:** Requerida (cualquier rol)

Envía una solicitud de amistad.

**Body:**
```json
{ "friend_id": 8 }
```

**Respuesta 201:** Objeto `Friendship` con `status: "PENDIENTE"`.

---

### `GET /api/friends/requests/`
**Auth:** Requerida (cualquier rol)

Solicitudes de amistad recibidas y pendientes.

**Respuesta 200:** Array de `Friendship`.

---

### `GET /api/friends/requests/sent/`
**Auth:** Requerida (cualquier rol)

Solicitudes de amistad enviadas y aún pendientes.

**Respuesta 200:** Array de `Friendship`.

---

### `PATCH /api/friends/request/{id}/accept/`
**Auth:** Requerida (debe ser el receptor de la solicitud)

Acepta una solicitud de amistad. Crea el vínculo bidireccional.

**Body:** Ninguno

**Respuesta 200:** Objeto `Friendship` con `status: "ACEPTADO"`.

---

### `DELETE /api/friends/request/{id}/reject/`
**Auth:** Requerida (debe ser el receptor de la solicitud)

Rechaza y elimina una solicitud de amistad pendiente.

**Body:** Ninguno

**Respuesta 204:** Sin contenido.

---

### `DELETE /api/friends/{id}/`
**Auth:** Requerida (cualquier rol)

Elimina una amistad. Elimina el vínculo en ambas direcciones.

**Body:** Ninguno

**Respuesta 204:** Sin contenido.

---

## Coaching

### `GET /api/coaching/entrenadores/?q=<string>`
**Auth:** Ninguna (pública)

Busca entrenadores por nombre, apellido o correo.

**Query param:** `q`

**Respuesta 200:**
```json
[
  {
    "id": 2,
    "nombre": "string",
    "apellidoPaterno": "string",
    "apellidoMaterno": "string",
    "correo": "email"
  }
]
```

---

### `GET /api/coaching/jugadores/`
**Auth:** `ENTRENADOR`

Retorna todos los jugadores asignados al entrenador autenticado.

**Respuesta 200:**
```json
[
  {
    "id": 5,
    "nombre": "string",
    "apellidoPaterno": "string",
    "apellidoMaterno": "string",
    "correo": "email",
    "nivelUsuario": "Amateur | Semi-Pro | Profesional | null"
  }
]
```

---

### `PATCH /api/coaching/jugadores/{id}/nivel/`
**Auth:** `ENTRENADOR`

Actualiza el nivel de uno de sus jugadores asignados.

**Body:**
```json
{ "nivel": "Amateur | Semi-Pro | Profesional" }
```

**Respuesta 200:**
```json
{ "id": 5, "nivelUsuario": "Semi-Pro" }
```

---

### `GET /api/coaching/jugadores/buscar/?q=<string>`
**Auth:** Requerida (cualquier rol)

Busca jugadores por nombre o apellido. Incluye nombre del entrenador asignado si tiene.

**Query param:** `q`

**Respuesta 200:**
```json
[
  {
    "id": 5,
    "nombre": "string",
    "apellidoPaterno": "string",
    "entrenador_nombre": "Carlos Pérez | null"
  }
]
```

---

### `POST /api/coaching/solicitudes/`
**Auth:** `JUGADOR`

El jugador envía una solicitud de asociación a un entrenador. Solo se puede tener un entrenador a la vez y una solicitud pendiente por entrenador.

**Body:**
```json
{ "entrenador_id": 2 }
```

**Respuesta 201:**
```json
{
  "id": 1,
  "jugador": { "id", "nombre", "apellidoPaterno", "apellidoMaterno", "correo" },
  "entrenador": { "id", "nombre", "apellidoPaterno", "apellidoMaterno", "correo" },
  "status": "PENDIENTE",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

### `GET /api/coaching/solicitudes/enviadas/`
**Auth:** `JUGADOR`

Solicitudes de asociación enviadas por el jugador autenticado.

**Respuesta 200:** Array de `SolicitudAsociacion`.

---

### `GET /api/coaching/solicitudes/recibidas/`
**Auth:** `ENTRENADOR`

Solicitudes de asociación pendientes recibidas por el entrenador autenticado.

**Respuesta 200:** Array de `SolicitudAsociacion`.

---

### `PATCH /api/coaching/solicitudes/{id}/aceptar/`
**Auth:** `ENTRENADOR`

Acepta una solicitud de asociación. Asigna el nivel al jugador y lo vincula al entrenador.

**Body:**
```json
{ "nivel": "Amateur | Semi-Pro | Profesional" }
```

**Respuesta 200:**
```json
{
  "id": 1,
  "jugador": { "id", "nombre", "apellidoPaterno", "apellidoMaterno", "correo" },
  "status": "ACEPTADA",
  "nivel_asignado": "Amateur"
}
```

---

### `PATCH /api/coaching/solicitudes/{id}/rechazar/`
**Auth:** `ENTRENADOR`

Rechaza una solicitud de asociación pendiente.

**Body:** Ninguno

**Respuesta 200:**
```json
{ "id": 1, "status": "RECHAZADA" }
```

---

### `GET /api/coaching/dashboard/`
**Auth:** `ENTRENADOR`

Retorna los últimos 5 partidos finalizados de todos los jugadores asignados al entrenador, con el marcador desde la perspectiva del jugador.

**Respuesta 200:**
```json
{
  "partidos": [
    {
      "id_match": "uuid",
      "jugador": {
        "id": 5,
        "nombre": "string",
        "apellidoPaterno": "string",
        "nivelUsuario": "Amateur"
      },
      "oponente": {
        "nombre": "string",
        "apellidoPaterno": "string",
        "es_invitado": false
      },
      "marcador_global": { "jugador": 2, "oponente": 1 },
      "sets": [
        { "set_number": 1, "jugador": 6, "oponente": 4 },
        { "set_number": 2, "jugador": 3, "oponente": 6 },
        { "set_number": 3, "jugador": 6, "oponente": 2 }
      ],
      "duration": 5400,
      "location": "string",
      "surface": "Clay | Hard",
      "created_at": "datetime"
    }
  ]
}
```
