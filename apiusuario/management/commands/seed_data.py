from datetime import date, datetime, timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from apiusuario.models import NivelUsuario, RolUsuario, SexoUsuario, Usuario
from coaching.models import EstadoSolicitud, SolicitudAsociacion
from matches.models import (
    BestOf,
    MatchData,
    MatchGame,
    MatchPoint,
    MatchScore,
    MatchSet,
    MatchState,
)

# ── Point patterns ──────────────────────────────────────────────────────────
# (p1_wins_point, score_p1_before, score_p2_before, duration_sec, bp_chance, bp_converted)

_P_HOLD_P1 = [   # p1 serves and holds (4-1)
    (True,  '0',  '0',  8,  False, False),
    (True,  '15', '0',  12, False, False),
    (False, '30', '0',  6,  False, False),
    (True,  '30', '15', 15, False, False),
    (True,  '40', '15', 10, False, False),
]

_P_HOLD_P2 = [   # p2 serves and holds, p1 loses (1-4)
    (False, '0',  '0',  9,  False, False),
    (False, '0',  '15', 14, False, False),
    (True,  '0',  '30', 7,  False, False),
    (False, '15', '30', 11, True,  False),  # bp chance for p1, not converted
    (False, '15', '40', 8,  False, False),
]

_P_BREAK_P1 = [  # p2 serves, p1 breaks (4-2)
    (True,  '0',  '0',  10, False, False),
    (False, '15', '0',  6,  False, False),
    (True,  '15', '15', 18, False, False),
    (False, '30', '15', 8,  False, False),
    (True,  '30', '30', 22, False, False),
    (True,  '40', '30', 15, True,  True),   # bp converted
]

_P_BREAK_P2 = [  # p1 serves, p2 breaks (2-4)
    (False, '0',  '0',  10, False, False),
    (True,  '0',  '15', 6,  False, False),
    (False, '15', '15', 18, False, False),
    (True,  '15', '30', 8,  False, False),
    (False, '30', '30', 22, False, False),
    (False, '30', '40', 15, True,  True),   # bp converted
]

_PATTERNS = {
    (True,  True):  _P_HOLD_P1,
    (False, False): _P_HOLD_P2,
    (True,  False): _P_BREAK_P1,
    (False, True):  _P_BREAK_P2,
}

# ── Set structures ──────────────────────────────────────────────────────────
# (p1_wins_game, server_is_p1, is_break)

_SET_1 = [  # p1 wins 6-3, p1 serves first
    (True,  True,  False),  # 1-0: hold p1
    (True,  False, True),   # 2-0: break p1
    (False, True,  True),   # 2-1: break p2
    (True,  False, True),   # 3-1: break p1
    (True,  True,  False),  # 4-1: hold p1
    (False, False, False),  # 4-2: hold p2
    (True,  True,  False),  # 5-2: hold p1
    (False, False, False),  # 5-3: hold p2
    (True,  True,  False),  # 6-3: hold p1
]

_SET_2 = [  # p1 loses 4-6, p2 serves first
    (False, False, False),  # 0-1: hold p2
    (True,  True,  False),  # 1-1: hold p1
    (False, False, False),  # 1-2: hold p2
    (False, True,  True),   # 1-3: break p2
    (True,  False, True),   # 2-3: break p1
    (True,  True,  False),  # 3-3: hold p1
    (False, False, False),  # 3-4: hold p2
    (True,  True,  False),  # 4-4: hold p1
    (False, False, False),  # 4-5: hold p2
    (False, True,  True),   # 4-6: break p2
]

_SET_3 = [  # p1 wins 6-4, p2 serves first
    (True,  False, True),   # 1-0: break p1
    (False, True,  True),   # 1-1: break p2
    (True,  False, True),   # 2-1: break p1
    (True,  True,  False),  # 3-1: hold p1
    (False, False, False),  # 3-2: hold p2
    (True,  True,  False),  # 4-2: hold p1
    (False, False, False),  # 4-3: hold p2
    (True,  True,  False),  # 5-3: hold p1
    (False, False, False),  # 5-4: hold p2
    (True,  True,  False),  # 6-4: hold p1
]

_SETS = [_SET_1, _SET_2, _SET_3]  # p1 wins 2-1


# ── Static data ─────────────────────────────────────────────────────────────

_COACHES = [
    {
        'nombre': 'Carlos', 'apellidoPaterno': 'Gómez', 'apellidoMaterno': 'Vidal',
        'correo': 'coach.carlos@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1980, 3, 15), 'password': 'Tennis2024!',
    },
    {
        'nombre': 'María', 'apellidoPaterno': 'Fernández', 'apellidoMaterno': 'Lagos',
        'correo': 'coach.maria@tennis.app', 'sexo': SexoUsuario.femenino,
        'fecha_nacimiento': date(1975, 7, 22), 'password': 'Tennis2024!',
    },
]

# coach_idx: 0 = Carlos, 1 = María
_PLAYERS = [
    # ── Carlos ──────────────────────────────────────────────────────────────
    {
        'nombre': 'Juan', 'apellidoPaterno': 'Pérez', 'apellidoMaterno': 'Mora',
        'correo': 'juan.perez@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1995, 5, 10), 'nivelUsuario': NivelUsuario.amateur,
        'altura': 180, 'peso': 78, 'password': 'Tennis2024!', 'coach_idx': 0,
    },
    {
        'nombre': 'Pedro', 'apellidoPaterno': 'Rojas', 'apellidoMaterno': 'Silva',
        'correo': 'pedro.rojas@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1993, 8, 20), 'nivelUsuario': NivelUsuario.semipro,
        'altura': 183, 'peso': 80, 'password': 'Tennis2024!', 'coach_idx': 0,
    },
    {
        'nombre': 'Diego', 'apellidoPaterno': 'Méndez', 'apellidoMaterno': 'Castro',
        'correo': 'diego.mendez@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1998, 2, 14), 'nivelUsuario': NivelUsuario.amateur,
        'altura': 175, 'peso': 72, 'password': 'Tennis2024!', 'coach_idx': 0,
    },
    {
        'nombre': 'Andrés', 'apellidoPaterno': 'Torres', 'apellidoMaterno': 'Navarro',
        'correo': 'andres.torres@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1991, 11, 3), 'nivelUsuario': NivelUsuario.pro,
        'altura': 188, 'peso': 85, 'password': 'Tennis2024!', 'coach_idx': 0,
    },
    {
        'nombre': 'Camila', 'apellidoPaterno': 'Ríos', 'apellidoMaterno': 'Jiménez',
        'correo': 'camila.rios@tennis.app', 'sexo': SexoUsuario.femenino,
        'fecha_nacimiento': date(1996, 4, 25), 'nivelUsuario': NivelUsuario.amateur,
        'altura': 165, 'peso': 58, 'password': 'Tennis2024!', 'coach_idx': 0,
    },
    # ── María ────────────────────────────────────────────────────────────────
    {
        'nombre': 'Valentina', 'apellidoPaterno': 'Cruz', 'apellidoMaterno': 'Reyes',
        'correo': 'valentina.cruz@tennis.app', 'sexo': SexoUsuario.femenino,
        'fecha_nacimiento': date(1994, 9, 18), 'nivelUsuario': NivelUsuario.semipro,
        'altura': 168, 'peso': 60, 'password': 'Tennis2024!', 'coach_idx': 1,
    },
    {
        'nombre': 'Sofía', 'apellidoPaterno': 'Medina', 'apellidoMaterno': 'Pérez',
        'correo': 'sofia.medina@tennis.app', 'sexo': SexoUsuario.femenino,
        'fecha_nacimiento': date(1999, 1, 8), 'nivelUsuario': NivelUsuario.amateur,
        'altura': 162, 'peso': 55, 'password': 'Tennis2024!', 'coach_idx': 1,
    },
    {
        'nombre': 'Lucas', 'apellidoPaterno': 'Vargas', 'apellidoMaterno': 'Ortega',
        'correo': 'lucas.vargas@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1997, 6, 30), 'nivelUsuario': NivelUsuario.amateur,
        'altura': 178, 'peso': 75, 'password': 'Tennis2024!', 'coach_idx': 1,
    },
    {
        'nombre': 'Tomás', 'apellidoPaterno': 'Herrera', 'apellidoMaterno': 'Soto',
        'correo': 'tomas.herrera@tennis.app', 'sexo': SexoUsuario.masculino,
        'fecha_nacimiento': date(1992, 12, 5), 'nivelUsuario': NivelUsuario.semipro,
        'altura': 185, 'peso': 82, 'password': 'Tennis2024!', 'coach_idx': 1,
    },
    {
        'nombre': 'Isabella', 'apellidoPaterno': 'Morales', 'apellidoMaterno': 'Lara',
        'correo': 'isabella.morales@tennis.app', 'sexo': SexoUsuario.femenino,
        'fecha_nacimiento': date(1990, 7, 15), 'nivelUsuario': NivelUsuario.pro,
        'altura': 170, 'peso': 62, 'password': 'Tennis2024!', 'coach_idx': 1,
    },
]

# local_idx wins each match (p1 = local in _SETS logic)
_PAIRINGS = [
    {'local': 0, 'invited': 5, 'surface': 'Clay', 'location': 'Club Tenis Santiago',
     'at': datetime(2025, 5, 1, 10, 0, tzinfo=timezone.utc)},   # Juan vs Valentina
    {'local': 1, 'invited': 6, 'surface': 'Hard', 'location': 'Club Tenis Providencia',
     'at': datetime(2025, 5, 3, 14, 0, tzinfo=timezone.utc)},   # Pedro vs Sofía
    {'local': 7, 'invited': 2, 'surface': 'Hard', 'location': 'Club Deportivo Municipal',
     'at': datetime(2025, 5, 6, 9, 0, tzinfo=timezone.utc)},    # Lucas vs Diego
    {'local': 3, 'invited': 8, 'surface': 'Hard', 'location': 'Club Tenis Las Condes',
     'at': datetime(2025, 5, 7, 11, 0, tzinfo=timezone.utc)},   # Andrés vs Tomás
    {'local': 9, 'invited': 4, 'surface': 'Clay', 'location': 'Club Tenis Las Condes',
     'at': datetime(2025, 5, 10, 14, 30, tzinfo=timezone.utc)}, # Isabella vs Camila
]


class Command(BaseCommand):
    help = 'Seeds the DB: 2 coaches, 5 players each, 1 finished match per player pair.'

    def handle(self, *args, **kwargs):
        if Usuario.objects.filter(correo='coach.carlos@tennis.app').exists():
            self.stdout.write(self.style.WARNING('Seed data already exists. Skipping.'))
            return

        with transaction.atomic():
            coaches = self._create_coaches()
            players = self._create_players(coaches)
            self._create_associations(players)
            self._create_matches(players)

        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(coaches)} coaches, {len(players)} players, {len(_PAIRINGS)} matches.'
        ))

    # ── Creators ────────────────────────────────────────────────────────────

    def _create_coaches(self):
        coaches = []
        for d in _COACHES:
            u = Usuario(
                rol=RolUsuario.entrenador,
                nombre=d['nombre'], apellidoPaterno=d['apellidoPaterno'],
                apellidoMaterno=d['apellidoMaterno'], correo=d['correo'],
                sexo=d['sexo'], fecha_nacimiento=d['fecha_nacimiento'],
            )
            u.set_password(d['password'])
            u.save()
            coaches.append(u)
        return coaches

    def _create_players(self, coaches):
        players = []
        for d in _PLAYERS:
            u = Usuario(
                rol=RolUsuario.jugador,
                nombre=d['nombre'], apellidoPaterno=d['apellidoPaterno'],
                apellidoMaterno=d['apellidoMaterno'], correo=d['correo'],
                sexo=d['sexo'], fecha_nacimiento=d['fecha_nacimiento'],
                nivelUsuario=d['nivelUsuario'], altura=d['altura'], peso=d['peso'],
                entrenador=coaches[d['coach_idx']],
            )
            u.set_password(d['password'])
            u.save()
            players.append(u)
        return players

    def _create_associations(self, players):
        for p in players:
            SolicitudAsociacion.objects.create(
                jugador=p,
                entrenador=p.entrenador,
                status=EstadoSolicitud.aceptada,
            )

    def _create_matches(self, players):
        for pairing in _PAIRINGS:
            p1 = players[pairing['local']]
            p2 = players[pairing['invited']]
            self._build_match(p1, p2, p1.entrenador, pairing)

    # ── Match builder ────────────────────────────────────────────────────────

    def _build_match(self, p1, p2, coach, pairing):
        match = MatchData.objects.create(
            id_local_player=p1,
            id_invited_player=p2,
            id_entrenador=coach,
            location=pairing['location'],
            surface=pairing['surface'],
            best_of=BestOf.THREE,
            match_state=MatchState.FINALIZADA,
            scheduled_at=pairing['at'],
        )

        score = MatchScore.objects.create(id_partido=match, winner_id=p1)
        total_duration = 0

        for set_games in _SETS:
            set_obj, set_duration = self._build_set(score, p1, p2, set_games)
            total_duration += set_duration

        score.duration = total_duration
        score.save()

        match.id_match_score = score
        match.save()

    def _build_set(self, score, p1, p2, set_games):
        p1_wins = sum(1 for g in set_games if g[0])
        p2_wins = len(set_games) - p1_wins
        set_winner = p1 if p1_wins > p2_wins else p2

        set_obj = MatchSet.objects.create(
            id_match_score=score,
            score_p1=p1_wins,
            score_p2=p2_wins,
            winner_id=set_winner,
            duration=0,
        )

        set_duration = 0
        for game_p1_wins, server_is_p1, is_break in set_games:
            game_duration = self._build_game(set_obj, p1, p2, game_p1_wins, server_is_p1, is_break)
            set_duration += game_duration

        set_obj.duration = set_duration
        set_obj.save()
        return set_obj, set_duration

    def _build_game(self, set_obj, p1, p2, game_p1_wins, server_is_p1, is_break):
        server = p1 if server_is_p1 else p2
        game_winner = p1 if game_p1_wins else p2
        points_data = _PATTERNS[(game_p1_wins, server_is_p1)]

        p1_pts = sum(1 for pt in points_data if pt[0])
        p2_pts = len(points_data) - p1_pts
        game_duration = sum(pt[3] for pt in points_data)

        game = MatchGame.objects.create(
            id_set=set_obj,
            p1_game_final_score=p1_pts,
            p2_game_final_score=p2_pts,
            duration=game_duration,
            winner_id=game_winner,
            is_break=is_break,
            is_tiebreak=False,
            is_serving=server,
        )

        for pt_p1_wins, sc_p1, sc_p2, dur, bp_chance, bp in points_data:
            MatchPoint.objects.create(
                is_serving=server,
                id_game=game,
                id_player_1=p1,
                id_player_2=p2,
                winner_id=p1 if pt_p1_wins else p2,
                score_p1=sc_p1,
                score_p2=sc_p2,
                duration=dur,
                break_point_chance=bp_chance,
                break_point=bp,
            )

        return game_duration
