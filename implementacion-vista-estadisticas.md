# Instrucciones: Vistas de Estadísticas

---

## Stats de un partido individual

```
GET /api/statistics/match/<uuid>/
Authorization: Bearer <access_token>
```

### Respuesta

```json
{
  "match_duration": "01:23:45",

  "points_win_loss": {
    "won": 45,
    "lost": 38,
    "total": 83,
    "won_pct": 54.2,
    "lost_pct": 45.8
  },

  "avg_duration_won": "00:08",
  "avg_duration_lost": "00:11",

  "break_points": {
    "generated": 8,
    "converted": 5,
    "conversion_pct": 62.5,
    "faced": 6,
    "saved": 4,
    "save_pct": 66.7
  },

  "total_distance": 856.34,

  "quartiles": [
    { "quartile": 1, "color": "green",  "min_duration": 2,  "max_duration": 5,  "count": 21, "pct": 25.3 },
    { "quartile": 2, "color": "yellow", "min_duration": 5,  "max_duration": 9,  "count": 20, "pct": 24.1 },
    { "quartile": 3, "color": "orange", "min_duration": 9,  "max_duration": 14, "count": 22, "pct": 26.5 },
    { "quartile": 4, "color": "red",    "min_duration": 14, "max_duration": 31, "count": 20, "pct": 24.1 }
  ],

  "points_per_interval": [
    { "interval": 5,  "points_won": 8 },
    { "interval": 10, "points_won": 6 },
    { "interval": 15, "points_won": 9 },
    { "interval": 20, "points_won": 5 }
  ],

  "distance_per_interval": [
    { "interval": 5,  "distance": 124.50 },
    { "interval": 10, "distance": 98.30 },
    { "interval": 15, "distance": 143.20 },
    { "interval": 20, "distance": 87.60 }
  ]
}
```

### Notas
- Solo disponible para partidos con `match_state: "FINALIZADA"`. Cualquier otro estado devuelve `400`.
- `avg_duration_won` y `avg_duration_lost` pueden ser `null` si no hay puntos en esa categoría.
- `match_duration` puede ser `null` si el partido no fue cerrado correctamente con `/finish/`.
- `quartile: 1` = puntos más cortos (verde, más efectivos). `quartile: 4` = más largos (rojo).
- `min_duration` / `max_duration` en segundos.
- `interval` = minuto de corte del intervalo (5 = primeros 5 min, 10 = minutos 5–10, etc.).

---

## Stats globales (últimos 14 partidos finalizados)

```
GET /api/statistics/global/
Authorization: Bearer <access_token>
```

### Respuesta

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
    "match_id": "550e8400-e29b-41d4-a716-446655440000",
    "won": true,
    "opponent": {
      "id": 2,
      "nombre": "Carlos",
      "apellidoPaterno": "López"
    },
    "location": "Club de Tenis Santiago",
    "surface": "Clay"
  },

  "total_distance": 12456.78,

  "avg_duration_won": "00:09",
  "avg_duration_lost": "00:12",

  "points_win_loss": {
    "won": 612,
    "lost": 524,
    "total": 1136,
    "won_pct": 53.9,
    "lost_pct": 46.1
  },

  "break_points": {
    "generated": 98,
    "converted": 61,
    "conversion_pct": 62.2,
    "faced": 87,
    "saved": 54,
    "save_pct": 62.1
  },

  "quartiles": [
    { "quartile": 1, "color": "green",  "min_duration": 1,  "max_duration": 6,  "count": 284, "pct": 25.0 },
    { "quartile": 2, "color": "yellow", "min_duration": 6,  "max_duration": 10, "count": 284, "pct": 25.0 },
    { "quartile": 3, "color": "orange", "min_duration": 10, "max_duration": 15, "count": 284, "pct": 25.0 },
    { "quartile": 4, "color": "red",    "min_duration": 15, "max_duration": 42, "count": 284, "pct": 25.0 }
  ],

  "points_per_interval": [
    { "interval": 5,  "points_won_avg": 7.2 },
    { "interval": 10, "points_won_avg": 6.8 },
    { "interval": 15, "points_won_avg": 8.1 },
    { "interval": 20, "points_won_avg": 5.4 }
  ],

  "distance_per_interval": [
    { "interval": 5,  "distance_avg": 118.40 },
    { "interval": 10, "distance_avg": 102.70 },
    { "interval": 15, "distance_avg": 134.90 },
    { "interval": 20, "distance_avg": 89.20 }
  ]
}
```

### Notas
- Si el usuario no tiene partidos finalizados devuelve `200` con `{ "message": "Sin partidos finalizados aún." }` — manejar este caso mostrando un estado vacío.
- `points_per_interval` y `distance_per_interval` son **promedios** entre los 14 partidos, no totales.
- `last_result.won: true` = el usuario autenticado ganó ese partido.
- Los cuartiles se calculan sobre el universo total de puntos de los 14 partidos.

---

## Errores comunes

| Código | Causa | Qué mostrar |
|---|---|---|
| `400` | Partido no finalizado (stats individuales) | "Las estadísticas solo están disponibles al finalizar el partido." |
| `403` | No sos participante | "No tenés acceso a estas estadísticas." |
| `404` | Partido no encontrado | "Partido no encontrado." |
