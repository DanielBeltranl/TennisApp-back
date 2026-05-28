# Data Model — TennisApp

> SQL DDL compatible con dbdiagram.io, DrawSQL y similares.

```sql
-- ─────────────────────────────────────────────
-- USUARIOS
-- ─────────────────────────────────────────────

CREATE TABLE usuario (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(100)  NOT NULL,
    apellidoPaterno  VARCHAR(100)  NOT NULL,
    apellidoMaterno  VARCHAR(100)  NOT NULL,
    correo           VARCHAR(254)  NOT NULL UNIQUE,
    password         VARCHAR(128)  NOT NULL,
    rol              VARCHAR(20)   NOT NULL,   -- 'Jugador' | 'Entrenador'
    sexo             VARCHAR(10),              -- 'Masculino' | 'Femenino' | 'Otro'
    fecha_nacimiento DATE,
    altura           INTEGER,
    peso             INTEGER,
    nivelUsuario     VARCHAR(20),              -- 'Amateur' | 'Semi-Pro' | 'Profesional'
    entrenador_id    INTEGER REFERENCES usuario(id) ON DELETE SET NULL,
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    last_login       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- SESIONES DE TOKEN
-- ─────────────────────────────────────────────

CREATE TABLE token_session (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    access_token  TEXT         NOT NULL,
    refresh_token TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ  NOT NULL,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    ip_address    INET,
    user_agent    VARCHAR(255)
);

-- ─────────────────────────────────────────────
-- MATCHES
-- ─────────────────────────────────────────────

CREATE TABLE match_data (
    id_match         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_local_player  INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    id_invited_player INTEGER     REFERENCES usuario(id) ON DELETE SET NULL,
    id_entrenador    INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    guest_name       VARCHAR(100),
    location         VARCHAR(100) NOT NULL,
    surface          VARCHAR(50)  NOT NULL,  -- 'Clay' | 'Hard'
    id_match_score   UUID         REFERENCES match_score(id_match_score) ON DELETE SET NULL,
    best_of          INTEGER      NOT NULL,  -- 1 | 3 | 5
    match_state      VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE',  -- PENDIENTE | ACEPTADO | INICIADO | PAUSADO | FINALIZADA
    scheduled_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE match_score (
    id_match_score  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_partido      UUID         NOT NULL UNIQUE REFERENCES match_data(id_match) ON DELETE CASCADE,
    winner_id       INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    duration        INTEGER,     -- segundos
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE match_set (
    id_set          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_match_score  UUID         NOT NULL REFERENCES match_score(id_match_score) ON DELETE CASCADE,
    score_p1        INTEGER      NOT NULL DEFAULT 0,
    score_p2        INTEGER      NOT NULL DEFAULT 0,
    winner_id       INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    duration        INTEGER,     -- segundos
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE match_game (
    id_game              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_set               UUID         NOT NULL REFERENCES match_set(id_set) ON DELETE CASCADE,
    p1_game_final_score  INTEGER,
    p2_game_final_score  INTEGER,
    duration             INTEGER,     -- segundos
    winner_id            INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    is_break             BOOLEAN,
    is_tiebreak          BOOLEAN      NOT NULL DEFAULT FALSE,
    is_serving           INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE match_point (
    id_point           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_game            UUID         NOT NULL REFERENCES match_game(id_game) ON DELETE CASCADE,
    is_serving         INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    id_player_1        INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    id_player_2        INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    winner_id          INTEGER      REFERENCES usuario(id) ON DELETE SET NULL,
    score_p1           VARCHAR(5)   NOT NULL,  -- '0' | '15' | '30' | '40' | 'AD'
    score_p2           VARCHAR(5)   NOT NULL,
    duration           INTEGER      NOT NULL,  -- segundos
    break_point_chance BOOLEAN      NOT NULL,
    break_point        BOOLEAN      NOT NULL,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- COACHING
-- ─────────────────────────────────────────────

CREATE TABLE solicitud_asociacion (
    id           SERIAL PRIMARY KEY,
    jugador_id   INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    entrenador_id INTEGER     NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    status       VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE',  -- PENDIENTE | ACEPTADA | RECHAZADA
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (jugador_id, entrenador_id)
);

-- ─────────────────────────────────────────────
-- AMISTAD
-- ─────────────────────────────────────────────

CREATE TABLE friendship (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    friend_id  INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    status     VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE',  -- PENDIENTE | ACEPTADO
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, friend_id)
);
```
