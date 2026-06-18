from django.test import TestCase

from apiusuario.models import RolUsuario, Usuario
from matches.models import BestOf, MatchData, MatchScore, MatchState
from statistics.calculators import calc_total_distance, get_global_stats


class FakePoint:
    def __init__(self, duration):
        self.duration = duration


class DistanceFormulaTests(TestCase):
    def test_total_distance_does_not_double_discount_effective_time(self):
        """point.duration is already pure ball-in-play time (no dead time
        between points is ever recorded), so the 'tiempo efectivo' percentage
        from tennis-math-data-and-logic.md must NOT be applied again here —
        that field only converts *total match clock* (which includes
        changeovers/pauses) into effective time. Applying it a second time on
        top of an already-effective duration silently shrinks results to a
        fraction of the real distance covered.
        """
        points = [FakePoint(duration=6144)]  # one 2-set match's worth, Amateur/Femenino/Clay

        distance = calc_total_distance(points, 'Amateur', 'Femenino', 'Clay')

        # mpm=25.0 for Amateur/Clay/Femenino -> 6144 * (25/60) = 2560.0
        self.assertAlmostEqual(distance, 2560.0, places=1)


class GlobalStatsGuestMatchTests(TestCase):
    def test_last_result_handles_guest_opponent_without_crashing(self):
        player = Usuario.objects.create_user(
            correo='guest-match-player@test.local', password='x',
            rol=RolUsuario.jugador, nombre='Test', apellidoPaterno='Player', apellidoMaterno='X',
        )

        match = MatchData.objects.create(
            id_local_player=player,
            id_invited_player=None,
            guest_name='Rival Invitado',
            location='Cancha de prueba',
            surface='Clay',
            best_of=BestOf.THREE,
            match_state=MatchState.FINALIZADA,
        )
        match_score = MatchScore.objects.create(id_partido=match, winner_id=player, duration=3600)
        match.id_match_score = match_score
        match.save()

        stats = get_global_stats([match], player.id, 'Amateur', 'Masculino')

        self.assertIsNotNone(stats['last_result'])
        self.assertIsNone(stats['last_result']['opponent']['id'])
        self.assertEqual(stats['last_result']['opponent']['nombre'], 'Rival Invitado')
