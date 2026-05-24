# Fase 5 — Dashboard del entrenador
> Un endpoint nuevo. Ningún endpoint anterior se modifica.

---

## Contexto

El entrenador ve los últimos 5 partidos finalizados de **todos sus jugadores combinados**, ordenados por fecha. Los scores siempre vienen desde la perspectiva del jugador del entrenador (`jugador` vs `oponente`), sin importar si el jugador fue creador o invitado del partido.

---

## Endpoint

### `GET /api/coaching/dashboard/`
> Solo accesible para entrenadores.

**Response `200` — con partidos**
```json
{
  "partidos": [
    {
      "id_match": "3f4a1b2c-...",
      "jugador": {
        "id": 5,
        "nombre": "Carlos",
        "apellidoPaterno": "González",
        "nivelUsuario": "Amateur"
      },
      "oponente": {
        "nombre": "Juan",
        "apellidoPaterno": "Martínez",
        "es_invitado": false
      },
      "marcador_global": {
        "jugador": 2,
        "oponente": 1
      },
      "sets": [
        { "set_number": 1, "jugador": 6, "oponente": 4 },
        { "set_number": 2, "jugador": 3, "oponente": 6 },
        { "set_number": 3, "jugador": 7, "oponente": 5 }
      ],
      "duration": 5400,
      "location": "Club Santa Lucía",
      "surface": "Clay",
      "created_at": "2026-05-20T10:00:00Z"
    }
  ]
}
```

**Response `200` — entrenador sin jugadores aún**
```json
{
  "partidos": []
}
```

---

## Detalle de campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `jugador.nivelUsuario` | `string` | Nivel del jugador al momento de la consulta |
| `oponente.es_invitado` | `boolean` | `true` si el oponente no tiene cuenta registrada |
| `marcador_global.jugador` | `integer` | Sets ganados por el jugador del entrenador |
| `marcador_global.oponente` | `integer` | Sets ganados por el oponente |
| `sets[].jugador` | `integer` | Games ganados por el jugador en ese set |
| `sets[].oponente` | `integer` | Games ganados por el oponente en ese set |
| `duration` | `integer \| null` | Duración total del partido en segundos |
| `surface` | `string` | `"Clay"` \| `"Hard"` |

---

## Caso con invitado sin cuenta

Cuando el oponente no tiene cuenta, `oponente.apellidoPaterno` viene vacío y `es_invitado: true`.

```json
{
  "oponente": {
    "nombre": "Pedro Soto",
    "apellidoPaterno": "",
    "es_invitado": true
  }
}
```

---

## Permisos

| Rol | Acceso |
|-----|--------|
| Entrenador | ✅ |
| Jugador | ❌ `403 Forbidden` |

---

## Notas para el front

- Los scores **siempre están normalizados** al jugador del entrenador — no hace falta saber si fue creador o invitado.
- El endpoint devuelve **máximo 5 partidos**, los más recientes primero.
- Solo incluye partidos con `match_state = FINALIZADA`.
- La pestaña de **solicitudes de asociación** del dashboard usa el endpoint ya existente: `GET /api/coaching/solicitudes/recibidas/` (documentado en Fase 3).
