# Consumir estadísticas globales — Jugador

## Endpoint

```
GET /api/statistics/global/
```

## Auth

Header obligatorio, igual que cualquier otro endpoint protegido:

```
Authorization: Bearer <access_token>
```

## Para un jugador: no se manda nada más

Si el JWT del usuario logueado tiene `rol: "Jugador"`, el backend ya sabe quién es (usa el usuario autenticado). **No hace falta mandar ningún query param.** Esto es solo para jugadores — si el usuario logueado es Entrenador, el backend exige `?player_id=<id>` (eso es otro caso, no aplica acá).

Ejemplo (fetch/axios):

```js
const res = await fetch('/api/statistics/global/', {
  headers: { Authorization: `Bearer ${accessToken}` },
});
const data = await res.json();
```

## Respuesta — caso con partidos

Toma los últimos 14 partidos `FINALIZADA` del jugador y devuelve:

```json
{
  "record": {
    "wins": 8,
    "losses": 6,
    "total": 14,
    "win_pct": 57.1,
    "loss_pct": 42.9
  },
  "last_result": {
    "match_id": "uuid",
    "won": true,
    "opponent": { "id": 12, "nombre": "...", "apellidoPaterno": "..." },
    "location": "Club Tenis Las Condes",
    "surface": "Clay"
  },
  "total_distance": 1234.56,
  "avg_duration_won": "00:24",
  "avg_duration_lost": "00:31",
  "points_win_loss": {
    "won": 320, "lost": 280, "total": 600,
    "won_pct": 53.3, "lost_pct": 46.7
  },
  "break_points": {
    "generated": 20, "converted": 9, "conversion_pct": 45.0,
    "faced": 15, "saved": 6, "save_pct": 40.0
  },
  "quartiles": [
    { "quartile": 1, "color": "green",  "min_duration": 3,  "max_duration": 12, "count": 150, "pct": 25.0 },
    { "quartile": 2, "color": "yellow", "min_duration": 12, "max_duration": 20, "count": 150, "pct": 25.0 },
    { "quartile": 3, "color": "orange", "min_duration": 20, "max_duration": 35, "count": 150, "pct": 25.0 },
    { "quartile": 4, "color": "red",    "min_duration": 35, "max_duration": 60, "count": 150, "pct": 25.0 }
  ],
  "points_per_interval": [
    { "interval": 5, "points_won_avg": 3.2 },
    { "interval": 10, "points_won_avg": 4.1 }
  ],
  "distance_per_interval": [
    { "interval": 5, "distance_avg": 85.4 },
    { "interval": 10, "distance_avg": 92.1 }
  ]
}
```

## Respuesta — sin partidos finalizados todavía

```json
{ "message": "Sin partidos finalizados aún." }
```

Status `200`, no es un error — hay que chequear si viene `message` en vez de `record` para mostrar el estado vacío en la UI.

## Errores posibles

| Status | Cuándo |
|---|---|
| 401 | Token ausente/expirado |

Para el rol Jugador no hay 400/403 — esos solo aplican cuando el que consulta es Entrenador sin `player_id` válido.
