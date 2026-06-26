"""Clears all match data and creates one finished guest match per existing player.

Safe to run multiple times. Does NOT touch users, coaches, or associations.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apiusuario.models import Usuario
from matches import models as matches_models
from matches.models import BestOf, MatchData, MatchScore, MatchState
from notifications.models import Notificacion, TipoNotificacion

from ._seed_demo_sim import GuestMatchSimulator

SURFACES = ['Clay', 'Hard']
LOCATIONS = [
    'Club Tenis Santiago',
    'Club Tenis Providencia',
    'Club Deportivo Municipal',
    'Club Tenis Las Condes',
]
GUEST_NAMES = [
    'Roberto Vega', 'Francisca Soto', 'Ignacio Bravo', 'Constanza Reyes',
    'Matías Fuentes', 'Javiera Contreras', 'Felipe Aguilar', 'Antonia Salinas',
    'Cristóbal Núñez', 'Daniela Pizarro', 'Rodrigo Parra', 'Elena Suárez',
]

PARTIDO_TIPOS = {
    TipoNotificacion.PARTIDO_AGENDADO,
    TipoNotificacion.PARTIDO_ACEPTADO,
    TipoNotificacion.PARTIDO_RECHAZADO,
    TipoNotificacion.PARTIDO_INICIADO,
    TipoNotificacion.PARTIDO_FINALIZADO,
}


class Command(BaseCommand):
    help = 'Clears all match data and reseeds one finished match per player.'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self._clear()
            players = list(Usuario.objects.filter(rol='Jugador').order_by('id'))
            if not players:
                self.stdout.write(self.style.WARNING('No players found. Nothing to seed.'))
                return
            self._create_matches(players)

        self.stdout.write(self.style.SUCCESS(
            f'Done: cleared old matches, created {len(players)} new matches.'
        ))

    def _clear(self):
        deleted_notifs, _ = Notificacion.objects.filter(tipo__in=PARTIDO_TIPOS).delete()
        deleted_matches, _ = MatchData.objects.all().delete()
        self.stdout.write(f'  Deleted {deleted_matches} matches, {deleted_notifs} notifications.')

    def _create_matches(self, players):
        now = timezone.now()
        for i, player in enumerate(players):
            surface  = SURFACES[i % len(SURFACES)]
            location = LOCATIONS[i % len(LOCATIONS)]
            guest    = GUEST_NAMES[i % len(GUEST_NAMES)]
            # Spread across the last ~13 days so history views look realistic
            scheduled_at = now - timedelta(days=13 - (i % 13), hours=i)
            self._build_match(player, surface, location, guest, scheduled_at)
            self.stdout.write(f'  Match created for {player.nombre} {player.apellidoPaterno}.')

    def _build_match(self, player, surface, location, guest_name, scheduled_at):
        match = MatchData.objects.create(
            id_local_player=player,
            id_invited_player=None,
            id_entrenador=getattr(player, 'entrenador', None),
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
        match_score.duration  = total_duration
        match_score.save()

        match.id_match_score = match_score
        match.match_state    = MatchState.FINALIZADA
        match.save()
