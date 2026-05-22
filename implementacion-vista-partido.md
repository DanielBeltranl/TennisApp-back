# Instrucciones: Módulo de Partidos Agendados

Este documento cubre dos vistas encadenadas:
1. **Vista de lista** — muestra todos los partidos del usuario separados por rol
2. **Vista de detalle** — muestra un partido específico con sus acciones disponibles

---

## VISTA 1 — Lista de partidos agendados

### Propósito

Pantalla con dos secciones que muestra los partidos del usuario autenticado separados por su rol: partidos que él creó y partidos a los que fue invitado.

### Endpoints

**Partidos que yo creé:**
```
GET /api/matches/my-created/
Authorization: Bearer <access_token>
```

**Partidos donde fui invitado:**
```
GET /api/matches/my-invited/
Authorization: Bearer <access_token>
```

Ambos devuelven un array ordenado del más reciente al más antiguo. Array vacío `[]` si no hay partidos.

### Forma de la respuesta (igual en ambos)

```json
[
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
    "score": null,
    "created_at": "2026-05-21T10:00:00Z",
    "updated_at": "2026-05-21T10:00:00Z"
  }
]
```

### Estructura de la vista

Dos secciones separadas (tabs o scroll con títulos):

**Sección "Mis partidos"** — usa `my-created/`

| Campo | Qué mostrar |
|---|---|
| `invited.nombre` + `invited.apellidoPaterno` | Rival |
| `location` | Lugar |
| `surface` | Superficie |
| `best_of` | Formato (ej. "Al mejor de 3") |
| `created_at` | Fecha |
| `match_state` | Chip de estado |

**Sección "Invitaciones"** — usa `my-invited/`

| Campo | Qué mostrar |
|---|---|
| `creator.nombre` + `creator.apellidoPaterno` | Rival |
| `location` | Lugar |
| `surface` | Superficie |
| `best_of` | Formato |
| `created_at` | Fecha |
| `match_state` | Chip de estado |

### Chips de estado

| `match_state` | Texto | Color sugerido |
|---|---|---|
| `PENDIENTE` | Pendiente | Amarillo |
| `ACEPTADO` | Aceptado | Azul |
| `INICIADO` | En curso | Verde |
| `PAUSADO` | Pausado | Naranja |
| `FINALIZADA` | Finalizado | Gris |

### Navegación

Al presionar cualquier tarjeta → navegar a la **Vista de detalle** (sección 2) pasando `id_match` como parámetro.

### Recarga

Llamar ambos endpoints al montar la vista y cada vez que el usuario regrese a esta pantalla desde la vista de detalle.

---

## VISTA 2 — Detalle del partido

### Propósito

Muestra la información completa de un partido y expone las acciones disponibles según el rol del usuario (creador o invitado) y el estado actual.

### Endpoint

```
GET /api/matches/match-data/<uuid>/
Authorization: Bearer <access_token>
```

### Datos a mostrar

| Campo | Qué mostrar |
|---|---|
| `creator.nombre` + `creator.apellidoPaterno` | Nombre del creador |
| `invited.nombre` + `invited.apellidoPaterno` | Nombre del invitado |
| `location` | Lugar del partido |
| `surface` | Superficie |
| `best_of` | Formato (`1`, `3` o `5` sets) |
| `match_state` | Estado actual |
| `created_at` | Fecha de agendamiento |

### Identificar el rol del usuario autenticado

```
si usuario_autenticado.id == respuesta.creator.id  →  soy el CREADOR
si usuario_autenticado.id == respuesta.invited.id  →  soy el INVITADO
```

El `id` del usuario autenticado viene del JWT o del endpoint `POST /api/usuarios/perfil/`.

### Lógica de botones

#### Soy el CREADOR

| `match_state` | Qué renderizar |
|---|---|
| `PENDIENTE` | Botón **"Pendiente"** — deshabilitado, no presionable, estilo apagado |
| `ACEPTADO` | Botón **"Comenzar partido"** — presionable → llama a `start` |
| `INICIADO` | Botón **"Continuar partido"** — presionable → navega a pantalla de juego |
| `PAUSADO` | Botón **"Reanudar partido"** — presionable → navega a pantalla de juego |
| `FINALIZADA` | Botón **"Ver resultado"** — presionable → navega al resumen |

#### Soy el INVITADO

| `match_state` | Qué renderizar |
|---|---|
| `PENDIENTE` | Dos botones: **"Aceptar"** y **"Rechazar"** |
| `ACEPTADO` | Botón **"Comenzar partido"** — presionable → llama a `start` |
| `INICIADO` | Botón **"Continuar partido"** — presionable → navega a pantalla de juego |
| `PAUSADO` | Botón **"Reanudar partido"** — presionable → navega a pantalla de juego |
| `FINALIZADA` | Botón **"Ver resultado"** — presionable → navega al resumen |

### Endpoints de cada acción

**Aceptar:**
```
PATCH /api/matches/<uuid>/accept/
Authorization: Bearer <access_token>
```
Respuesta `200` con el partido actualizado (`match_state: "ACEPTADO"`).

**Rechazar:**
```
DELETE /api/matches/<uuid>/reject/
Authorization: Bearer <access_token>
```
Respuesta `204` sin body. El registro se elimina de la base de datos.

**Comenzar partido:**
```
PATCH /api/matches/<uuid>/start/
Authorization: Bearer <access_token>
Content-Type: application/json

{ "first_server_id": <id del jugador que saca primero> }
```
Antes de llamar este endpoint mostrar un modal o selector para elegir quién saca primero (los dos jugadores disponibles están en `creator` e `invited`). Respuesta `200` con `match_state: "INICIADO"`.

**Pausar:**
```
PATCH /api/matches/<uuid>/pause/
Authorization: Bearer <access_token>
```

**Reanudar:**
```
PATCH /api/matches/<uuid>/resume/
Authorization: Bearer <access_token>
```

### Comportamiento de recarga automática

Este componente debe refrescar los datos del partido después de cada acción:

```
1. Usuario presiona un botón
2. Se ejecuta el endpoint correspondiente
3. Se vuelve a llamar GET /api/matches/match-data/<uuid>/
4. El componente se actualiza con el nuevo estado
```

No usar estado local para inferir el nuevo `match_state` — siempre leer desde el servidor.

### Manejo de errores

Todos los endpoints devuelven errores con este formato:
```json
{ "error": "Descripción del error." }
```

| Código | Situación | Mensaje en UI |
|---|---|---|
| `403` | No sos participante | "No tenés acceso a este partido." |
| `400` | Estado incorrecto para la acción | Mostrar el campo `error` directamente |
| `404` | Partido no encontrado | "El partido no existe o fue eliminado." |

### Notas

- `id_match` es **UUID** — usarlo tal cual en la URL.
- `score` viene `null` hasta que el partido es iniciado. No renderizarlo antes.
- Los estados `INICIADO` y `PAUSADO` navegan a la pantalla de juego. Pasar `id_match` como parámetro para que esa pantalla llame al endpoint de recovery:
  ```
  GET /api/matches/<uuid>/recovery/
  ```
