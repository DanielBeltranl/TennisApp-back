# Match Summary

Returns the last 5 finished matches for the authenticated player, ordered from most recent to oldest.

## Endpoint

```
GET /api/matches/summary/
```

## Auth

Requires a valid JWT in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Response

```json
[
  {
    "id_match": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "creator": {
      "id": 3,
      "nombre": "Daniel",
      "apellidoPaterno": "Beltran",
      "correo": "daniel@gmail.com"
    },
    "invited": {
      "id": 4,
      "nombre": "Maxi",
      "apellidoPaterno": "Huerta",
      "correo": "maxi@gmai.com"
    },
    "guest_name": null,
    "location": "Club Tenis Las Condes",
    "surface": "Clay",
    "best_of": 3,
    "match_state": "FINALIZADA",
    "winner": {
      "id": 3,
      "nombre": "Daniel",
      "apellidoPaterno": "Beltran",
      "correo": "daniel@gmail.com"
    },
    "duration": 3600,
    "sets": [
      {
        "score_p1": 6,
        "score_p2": 4,
        "games": [
          { "p1_game_final_score": 4, "p2_game_final_score": 0 },
          { "p1_game_final_score": 0, "p2_game_final_score": 4 }
        ]
      },
      {
        "score_p1": 6,
        "score_p2": 3,
        "games": [
          { "p1_game_final_score": 4, "p2_game_final_score": 2 }
        ]
      }
    ],
    "created_at": "2026-05-24T18:00:00Z"
  }
]
```

## Fields

| Campo | Descripción |
|-------|-------------|
| `id_match` | UUID del partido |
| `creator` | Jugador que creó el partido |
| `invited` | Jugador invitado (`null` si fue contra un guest) |
| `guest_name` | Nombre del rival si no era usuario registrado |
| `location` | Lugar donde se jugó |
| `surface` | Superficie (`Clay`, `Hard`, etc.) |
| `best_of` | Formato del partido (1, 3 o 5 sets) |
| `match_state` | Siempre `FINALIZADA` en este endpoint |
| `winner` | Jugador ganador |
| `duration` | Duración total en segundos |
| `sets` | Lista de sets con marcador y games internos |
| `created_at` | Fecha y hora del partido |

## Notes

- Only returns matches with `match_state = FINALIZADA`.
- Returns matches where the user participated as creator or invited.
- Maximum 5 results.
- `p1` always refers to the creator, `p2` to the invited player.
