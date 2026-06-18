from django.core.management import call_command
from django.test import TestCase

from apiusuario.models import RolUsuario, Usuario
from matches.models import MatchData, MatchState
from statistics.calculators import get_match_stats

DEMO_PASSWORD = 'Tennis2024!'


class SeedDemoCommandTests(TestCase):
    def test_is_idempotent(self):
        call_command('seed_demo')
        call_command('seed_demo')

        self.assertEqual(Usuario.objects.count(), 12)

    def test_creates_two_coaches_and_ten_players_five_each(self):
        call_command('seed_demo')

        coaches = Usuario.objects.filter(rol=RolUsuario.entrenador)
        players = Usuario.objects.filter(rol=RolUsuario.jugador)

        self.assertEqual(coaches.count(), 2)
        self.assertEqual(players.count(), 10)

        for coach in coaches:
            self.assertEqual(players.filter(entrenador=coach).count(), 5)

    def test_accounts_have_real_working_passwords(self):
        call_command('seed_demo')

        coach = Usuario.objects.filter(rol=RolUsuario.entrenador).first()
        player = Usuario.objects.filter(rol=RolUsuario.jugador).first()

        self.assertTrue(coach.has_usable_password())
        self.assertTrue(player.has_usable_password())
        self.assertTrue(coach.check_password(DEMO_PASSWORD))
        self.assertTrue(player.check_password(DEMO_PASSWORD))

    def test_each_player_has_one_finished_guest_match_with_points(self):
        call_command('seed_demo')

        players = Usuario.objects.filter(rol=RolUsuario.jugador)

        for player in players:
            matches = MatchData.objects.filter(id_local_player=player)
            self.assertEqual(matches.count(), 1)

            match = matches.first()
            self.assertEqual(match.match_state, MatchState.FINALIZADA)
            self.assertIsNone(match.id_invited_player)
            self.assertIsNotNone(match.guest_name)

            points = list(
                __import__('matches.models', fromlist=['MatchPoint']).MatchPoint.objects.filter(
                    id_game__id_set__id_match_score__id_partido=match
                )
            )
            self.assertGreater(len(points), 0)

    def test_seeded_match_produces_realistic_stats(self):
        call_command('seed_demo')

        from matches.models import MatchPoint

        player = Usuario.objects.filter(rol=RolUsuario.jugador).first()
        match = MatchData.objects.get(id_local_player=player)

        points = list(
            MatchPoint.objects.filter(
                id_game__id_set__id_match_score__id_partido=match
            ).order_by('created_at')
        )

        stats = get_match_stats(
            points,
            player.id,
            match.match_score,
            player.nivelUsuario,
            player.sexo,
            match.surface,
        )

        self.assertGreater(stats['points_win_loss']['total'], 0)
        self.assertGreater(stats['total_distance'], 0)
        self.assertTrue(len(stats['quartiles']) > 0)

    def test_sets_and_games_have_their_internal_scoreboard_populated(self):
        call_command('seed_demo')

        from matches.models import MatchGame, MatchSet

        player = Usuario.objects.filter(rol=RolUsuario.jugador).first()
        match = MatchData.objects.get(id_local_player=player)
        sets = list(MatchSet.objects.filter(id_match_score=match.match_score).order_by('created_at'))

        self.assertGreater(len(sets), 0)
        for s in sets:
            self.assertGreater(
                s.score_p1 + s.score_p2, 0,
                'MatchSet.score_p1/score_p2 (games won within the set) must be '
                'populated, not left at the 0/0 default.'
            )

            games = list(MatchGame.objects.filter(id_set=s).order_by('created_at'))
            last_game = games[-1]
            self.assertIsNotNone(
                last_game.p1_game_final_score,
                'MatchGame.p1_game_final_score must reflect the running set score, '
                'not be left null.'
            )
            self.assertIsNotNone(last_game.p2_game_final_score)
            self.assertEqual(
                {last_game.p1_game_final_score, last_game.p2_game_final_score},
                {s.score_p1, s.score_p2},
            )

    def test_point_timestamps_within_a_match_are_spread_out(self):
        call_command('seed_demo')

        from matches.models import MatchPoint

        player = Usuario.objects.filter(rol=RolUsuario.jugador).first()
        match = MatchData.objects.get(id_local_player=player)

        points = list(
            MatchPoint.objects.filter(
                id_game__id_set__id_match_score__id_partido=match
            ).order_by('created_at')
        )

        distinct_timestamps = {p.created_at for p in points}
        self.assertGreater(
            len(distinct_timestamps), 2,
            'MatchPoint.created_at must be backdated with a realistic spread, '
            'not left at auto_now_add insertion time.'
        )
