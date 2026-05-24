# Fase 4 — Partidos con invitado sin cuenta
> Solo cambia el endpoint de agendamiento y el registro de puntos. El resto del flujo de partido es igual.

---

## Contexto

Ahora se puede agendar un partido contra alguien que no tiene cuenta en la app. Se guarda solo su nombre para el resumen del partido. Las estadísticas se calculan **únicamente para el creador** — el invitado no tiene perfil, así que sus datos no se persisten.

**Reglas:**
- Se envía `id_player_invited` **O** `guest_name`, nunca ambos, nunca ninguno
- Los partidos con invitado se crean en estado `ACEPTADO` directamente (no hay nadie que acepte)
- Cuando el invitado gana un punto, `winner_id` va como `null` → cuenta como punto perdido para el creador en las estadísticas

---

## Endpoints modificados

### `POST /api/matches/schedule/`

#### Caso 1 — Partido con jugador registrado (sin cambios en lógica)
```json
{
  "id_player_invited": 3,
  "location": "Club Santa Lucía",
  "surface": "Clay",
  "best_of": 3
}
```
> Sigue requiriendo amistad. Se crea en estado `PENDIENTE`.

#### Caso 2 — Partido con invitado sin cuenta ← NUEVO
```json
{
  "guest_name": "Pedro Soto",
  "location": "Club Santa Lucía",
  "surface": "Clay",
  "best_of": 3
}
```
> Sin validación de amistad. Se crea en estado `ACEPTADO` directamente.

**Response `201` — partido con invitado**
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
  "match_state": "ACEPTADO",
  "created_at": "2026-05-23T14:00:00Z"
}
```

**Errores posibles**
```json
// Ambos campos enviados
{ "non_field_errors": ["Enviá id_player_invited o guest_name, no ambos."] }

// Ninguno enviado
{ "non_field_errors": ["Debés enviar id_player_invited o guest_name."] }
```

---

### `POST /api/matches/{id}/point/`

El campo `winner_id` ahora es **opcional** en partidos con invitado.

| Situación | Qué mandar |
|-----------|-----------|
| Creador gana el punto | `"winner_id": <id_del_creador>` |
| Invitado gana el punto | `"winner_id": null` o no mandar el campo |
| Partido normal (sin invitado) | `"winner_id"` sigue siendo obligatorio |

**Request — invitado ganó el punto**
```json
{
  "winner_id": null,
  "duration": 8
}
```

**Request — creador ganó el punto**
```json
{
  "winner_id": 1,
  "duration": 5
}
```

> El response de este endpoint no cambia.

**Error — winner_id inválido en partido con invitado**
```json
{ "error": "El ganador debe ser el creador o null (invitado)." }
```

---

### `PATCH /api/matches/{id}/finish/`

Para partidos con invitado, `winner_id` puede ser `null` (ganó el invitado) o el ID del creador.

**Request — creador ganó**
```json
{ "winner_id": 1 }
```

**Request — invitado ganó**
```json
{ "winner_id": null }
```
o simplemente no enviar el campo.

---

## Endpoints que NO aplican a partidos con invitado

| Endpoint | Respuesta si se llama con partido de invitado |
|----------|----------------------------------------------|
| `PATCH /api/matches/{id}/accept/` | `400 — Este partido no tiene jugador invitado registrado.` |
| `DELETE /api/matches/{id}/reject/` | `400 — Este partido no tiene jugador invitado registrado.` |

---

## Estado inicial según tipo de partido

| Tipo | Estado al crear |
|------|----------------|
| Con jugador registrado | `PENDIENTE` (espera que el invitado acepte) |
| Con invitado sin cuenta | `ACEPTADO` (listo para iniciar directo) |

---

## Cómo aparece en la pestaña de partidos agendados

El front ya filtra los partidos por estado. Como el partido con invitado nace en `ACEPTADO`, aparece directamente en la pestaña de "listos para iniciar" sin pasar por "pendientes".

---

## Comportamiento de las estadísticas

Cuando hay puntos con `winner_id: null` (invitado ganó), las estadísticas los tratan como **puntos perdidos por el creador**. No hay stats del lado del invitado. Todo lo demás (distancia, duración, break points, etc.) se calcula igual que siempre para el creador.
