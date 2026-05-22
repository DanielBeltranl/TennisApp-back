# Instrucciones: Pantalla de juego (registro de puntos)

Pantalla activa mientras un partido está en curso. Permite registrar punto a punto, deshacer errores, pausar y confirmar el cierre del partido.

---

## Al entrar a la pantalla

Siempre llamar primero al endpoint de recovery para reconstruir el estado actual (aplica tanto al entrar por primera vez como al reanudar un partido pausado):

```
GET /api/matches/<uuid>/recovery/
Authorization: Bearer <access_token>
```

**Forma de la respuesta:**
```json
{
  "match": { "id_match": "...", "best_of": 3, "match_state": "INICIADO", "..." },
  "sets_p1": 1,
  "sets_p2": 0,
  "sets": [
    { "id_set": "...", "set_number": 1, "score_p1": 6, "score_p2": 4, "winner_id": 1 }
  ],
  "current_set": { "id_set": "...", "set_number": 2, "score_p1": 2, "score_p2": 3 },
  "current_game": {
    "id_game": "...",
    "game_number": 6,
    "is_serving": { "id": 2, "nombre": "Carlos", "apellidoPaterno": "López" }
  },
  "current_score": { "score_p1": "30", "score_p2": "15" },
  "last_point": {
    "id_point": "...",
    "score_p1": "30",
    "score_p2": "15",
    "winner_id": 1,
    "duration": 8,
    "created_at": "2026-05-21T14:32:00Z"
  }
}
```

- `last_point` puede ser `null` si el game no tiene puntos aún.
- `current_game` y `current_set` pueden ser `null` — manejar como error y mostrar mensaje.
- Usar `current_score` para inicializar el marcador en pantalla.
- Si `current_game.is_tiebreak == true` al entrar, arrancar directamente en modo tiebreak (ver sección **Tiebreak**).

---

## Registrar un punto

```
POST /api/matches/<uuid>/point/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "winner_id": <id del jugador que ganó el punto>,
  "duration": <duración del punto en segundos (entero)>
}
```

**Cronómetro:** iniciar al comenzar cada punto y detenerlo cuando el usuario presiona el botón del ganador. Enviar el valor en `duration`.

---

## Forma de la respuesta y qué hacer con ella

La respuesta siempre incluye estos flags:

```json
{
  "game_closed": false,
  "set_closed": false,
  "match_closed": false,
  "tiebreak_required": false,
  "point": { "..." },
  "current_score": { "score_p1": "30", "score_p2": "15" },
  "current_game": { "id_game": "...", "is_serving_id": 1, "is_tiebreak": false },
  "current_set": { "score_p1": 2, "score_p2": 3 }
}
```

Leer los flags en orden. El primero en `true` determina qué mostrar:

| Flag | Situación | Qué hacer |
|---|---|---|
| Todos `false` | Punto anotado, game sigue | Actualizar `current_score` en pantalla y continuar |
| `game_closed: true` | Se cerró el game | Actualizar marcador de games (`current_set`) y mostrar brevemente quién ganó |
| `set_closed: true` | Se cerró el set | Mostrar resultado del set y actualizar `sets_p1` / `sets_p2` |
| `tiebreak_required: true` | Set en 6-6, arranca tiebreak | Ver sección **Tiebreak** abajo |
| `match_closed: true` | El marcador indica un ganador | Ver sección **Cierre de partido** abajo |

**Nunca** inferir el estado desde el cliente — siempre usar los flags de la respuesta.

---

## Marcador en pantalla

**Game normal** — mostrar `score_p1` y `score_p2` con los valores del tenis: `0`, `15`, `30`, `40`, `AD`.

**Tiebreak** — cuando `current_game.is_tiebreak == true`, mostrar como números enteros: `0`, `1`, `2` … sin límite superior fijo.

**Servidor** — `current_game.is_serving_id` indica quién saca en el game. En tiebreak, el servidor rota internamente en el backend — el frontend no necesita calcularlo.

---

## Tiebreak

Cuando la respuesta incluye `tiebreak_required: true`:

1. El set quedó 6-6. El backend ya creó el game de tiebreak.
2. La respuesta incluye `current_game.is_tiebreak: true` y el nuevo `id_game`.
3. Guardar el nuevo `id_game` en el estado local (aunque no se envía en el request de punto — el backend lo resuelve solo).
4. Cambiar el display del marcador de `0/15/30/40/AD` a números enteros.
5. Mostrar un indicador visual de tiebreak (ej. badge "Tiebreak").
6. El tiebreak termina cuando llega `game_closed: true` + `set_closed: true` (set cerrado 7-6).

---

## Deshacer último punto

Botón siempre visible mientras el partido está en `INICIADO`.

```
DELETE /api/matches/<uuid>/point/undo/
Authorization: Bearer <access_token>
```

Respuesta `200`:
```json
{ "mensaje": "Punto deshecho." }
```

Después de cualquier undo, llamar a recovery para reconstruir el estado completo — el undo puede haber revertido un game, un set, o el cierre del partido.

---

## Pausar partido

Botón siempre visible mientras el partido está en `INICIADO`.

```
PATCH /api/matches/<uuid>/pause/
Authorization: Bearer <access_token>
```

Respuesta `200` con `match_state: "PAUSADO"`. Navegar de regreso a la vista de detalle del partido.

---

## Cierre de partido

Cuando la respuesta contiene `match_closed: true`:

- **NO** finalizar el partido automáticamente.
- Mostrar el marcador final y un botón prominente **"Terminar partido"**.
- Mantener visible el botón **"Deshacer"** — el usuario puede corregir el marcador antes de confirmar.

Solo cuando el usuario presiona **"Terminar partido"**, llamar:

```
PATCH /api/matches/<uuid>/finish/
Authorization: Bearer <access_token>
Content-Type: application/json

{ "winner_id": <id del jugador ganador> }
```

El `winner_id` se obtiene de `response_data.winner.id` que llegó en la respuesta del último punto registrado. Guardarlo en estado local al recibir `match_closed: true`.

Respuesta `200` con `match_state: "FINALIZADA"`. Navegar al resumen del partido.

> **Por qué este flujo:** si el marcador se ingresó mal, el usuario tiene la chance de deshacer puntos antes de confirmar. El `/finish/` es el acto explícito de cerrar la sesión, no un efecto secundario automático.

---

## Manejo de errores

| Código | Causa | Qué mostrar |
|---|---|---|
| `400` | No hay game/set activo, partido no en curso | Mostrar campo `error` de la respuesta |
| `403` | No sos participante | "No tenés acceso a este partido." |
| `404` | Partido o jugador no encontrado | "Partido no encontrado." |
