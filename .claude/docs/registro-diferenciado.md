# Fase 2 — Registro diferenciado por rol
> Cambios en el endpoint de registro. El resto de la API no se toca.

---

## Qué cambió y por qué

El registro ahora bifurca según el `rol` que se envíe. El backend selecciona las validaciones correspondientes y devuelve errores específicos si falta algún campo obligatorio para ese rol.

---

## Endpoint afectado

### `POST /api/usuarios/registro/`

El campo `rol` es ahora **el primero que el backend lee**. Si no viene o es inválido, la request se rechaza antes de validar cualquier otra cosa.

---

## Caso 1 — Registro JUGADOR

**Campos obligatorios**
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

**Response exitoso `201`**
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
  "access": "<jwt>",
  "refresh": "<jwt>",
  "mensaje": "Usuario registrado exitosamente"
}
```

> `nivelUsuario` siempre llega `null` al registrarse. Un entrenador lo asigna después (Fase 3).

---

## Caso 2 — Registro ENTRENADOR

**Campos obligatorios**
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

> `sexo`, `altura` y `peso` **no se envían**. El backend los guarda como `null`.

**Response exitoso `201`**
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
  "access": "<jwt>",
  "refresh": "<jwt>",
  "mensaje": "Usuario registrado exitosamente"
}
```

---

## Errores posibles

### `rol` inválido o ausente → `400`
```json
{
  "rol": "Valor inválido. Opciones: ['Jugador', 'Entrenador']"
}
```

### Campo obligatorio faltante en JUGADOR → `400`
```json
{
  "sexo": "Este campo es obligatorio para jugadores.",
  "altura": "Este campo es obligatorio para jugadores."
}
```

### Campo obligatorio faltante en ENTRENADOR → `400`
```json
{
  "fecha_nacimiento": "Este campo es obligatorio para entrenadores."
}
```

### Correo duplicado → `400`
```json
{
  "correo": ["This field must be unique."]
}
```

---

## Valores válidos por campo

| Campo | Valores |
|-------|---------|
| `rol` | `"Jugador"` \| `"Entrenador"` |
| `sexo` | `"Masculino"` \| `"Femenino"` \| `"Otro"` |
| `fecha_nacimiento` | `"YYYY-MM-DD"` |
| `nivelUsuario` | No se envía en el registro |

---

## Flujo sugerido en el form de registro

```
1. Mostrar selector de rol (Jugador / Entrenador)
2. Si Jugador  → mostrar: nombre, apellidos, correo, password, sexo, fecha_nacimiento, altura, peso
3. Si Entrenador → mostrar: nombre, apellidos, correo, password, fecha_nacimiento
4. POST al endpoint con el body correspondiente
5. Si nivelUsuario === null en la respuesta → mostrar banner:
   "Tu entrenador aún no te ha asignado un nivel de juego"
```

---

## Sin cambios

- `POST /api/login/` — igual que antes
- `POST /api/token/refresh/` — igual que antes
- Todos los endpoints de matches, stats y friendship — sin cambios
