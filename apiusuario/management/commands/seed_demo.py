from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apiusuario.models import RolUsuario, Usuario
from coaching.models import EstadoSolicitud, SolicitudAsociacion
from matches import models as matches_models
from matches.models import BestOf, MatchData, MatchScore, MatchState

from ._seed_demo_data import COACHES, DEMO_PASSWORD, GUEST_NAMES, LOCATIONS, PLAYERS, SURFACES
from ._seed_demo_sim import GuestMatchSimulator


class Command(BaseCommand):
    help = (
        'Seeds demo data: 2 coaches, 5 players each, 1 finished guest match per '
        'player. Idempotent — safe to run on every container boot.'
    )

    def handle(self, *args, **kwargs):
        if Usuario.objects.filter(correo=COACHES[0]['correo']).exists():
            self.stdout.write(self.style.WARNING('Seed data already exists. Skipping.'))
            return

        with transaction.atomic():
            coaches = self._create_coaches()
            players = self._create_players(coaches)
            self._create_associations(players)
            self._create_matches(players)

        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(coaches)} coaches, {len(players)} players, {len(players)} matches.'
        ))

    # -- Creators --

    def _create_coaches(self):
        coaches = []
        for d in COACHES:
            u = Usuario(
                rol=RolUsuario.entrenador,
                nombre=d['nombre'], apellidoPaterno=d['apellidoPaterno'],
                apellidoMaterno=d['apellidoMaterno'], correo=d['correo'],
                sexo=d['sexo'], fecha_nacimiento=d['fecha_nacimiento'],
            )
            u.set_password(DEMO_PASSWORD)
            u.save()
            coaches.append(u)
        return coaches

    def _create_players(self, coaches):
        players = []
        for d in PLAYERS:
            u = Usuario(
                rol=RolUsuario.jugador,
                nombre=d['nombre'], apellidoPaterno=d['apellidoPaterno'],
                apellidoMaterno=d['apellidoMaterno'], correo=d['correo'],
                sexo=d['sexo'], fecha_nacimiento=d['fecha_nacimiento'],
                nivelUsuario=d['nivelUsuario'], altura=d['altura'], peso=d['peso'],
                entrenador=coaches[d['coach_idx']],
            )
            u.set_password(DEMO_PASSWORD)
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
        now = timezone.now()
        for i, player in enumerate(players):
            surface = SURFACES[i % len(SURFACES)]
            location = LOCATIONS[i % len(LOCATIONS)]
            guest_name = GUEST_NAMES[i % len(GUEST_NAMES)]
            # Stagger across the last ~13 days so "last N matches" views look realistic.
            scheduled_at = now - timedelta(days=13 - i, hours=i)
            self._build_match(player, surface, location, guest_name, scheduled_at)

    # -- Match builder --

    def _build_match(self, player, surface, location, guest_name, scheduled_at):
        match = MatchData.objects.create(
            id_local_player=player,
            id_invited_player=None,
            id_entrenador=player.entrenador,
            guest_name=guest_name,
            location=location,
            surface=surface,
            best_of=BestOf.THREE,
            match_state=MatchState.INICIADO,
            scheduled_at=scheduled_at,
        )

        match_score = MatchScore.objects.create(id_partido=match)

        simulator = GuestMatchSimulator(
            player=player,
            surface=surface,
            best_of=BestOf.THREE,
            scheduled_at=scheduled_at,
            models=matches_models,
        )
        total_duration, player_wins_match = simulator.simulate(match_score)

        match_score.winner_id = player if player_wins_match else None
        match_score.duration = total_duration
        match_score.save()

        match.id_match_score = match_score
        match.match_state = MatchState.FINALIZADA
        match.save()
