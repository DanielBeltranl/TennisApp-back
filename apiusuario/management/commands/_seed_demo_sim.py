"""Probabilistic point-by-point match simulator for seed_demo.

Drives the exact same functions matches/views.py uses in production
(advance_score, advance_tiebreak_score, is_break_point_chance, is_break_point,
is_set_over, is_match_over, get_next_server, get_tiebreak_server) so the
generated rows are structurally identical to what a real guest match would
produce. Mirrors the guest-match conventions from RegisterPointView/
FinishMatchView (matches/views.py ~122-270, ~413-620):

- is_serving (MatchGame/MatchPoint) is always the local player; the real
  server is tracked via MatchGame.guest_is_serving.
- id_player_2 is always None on MatchPoint for guest matches.
- server_is_creator = not current_game.guest_is_serving
- current_game.is_break = (current_game.guest_is_serving == winner_is_creator)
- guest_is_serving toggles every new game, starting False (local serves game 1).
- winner_id is the player's Usuario if they won, None if the guest won.
"""
import random
from datetime import timedelta

from matches.services import (
    advance_score,
    advance_tiebreak_score,
    is_break_point,
    is_break_point_chance,
    is_match_over,
    is_set_over,
)


def _point_duration(rng, surface):
    if surface == 'Clay':
        return rng.randint(8, 55)
    return rng.randint(6, 45)


class GuestMatchSimulator:
    """Simulates a finished guest match for a single local player.

    Builds MatchSet/MatchGame/MatchPoint rows via the model classes passed in
    by the caller (kept decoupled from the models module so this stays a pure
    simulation helper). Returns the built objects plus aggregate durations so
    the command can persist MatchScore/MatchData fields.
    """

    def __init__(self, player, surface, best_of, scheduled_at, models):
        self.player = player
        self.surface = surface
        self.best_of = best_of
        self.scheduled_at = scheduled_at
        self.models = models  # module: matches.models

        self.rng = random.Random(player.correo)
        self.p_win_own_serve = 0.62 + self.rng.uniform(-0.05, 0.05)
        self.p_win_on_return = 0.38 + self.rng.uniform(-0.05, 0.05)

        self._elapsed_seconds = 0
        self._all_points = []  # in-memory MatchPoint instances awaiting timestamp fix-up

    def _next_timestamp(self, duration):
        ts = self.scheduled_at + timedelta(seconds=self._elapsed_seconds)
        self._elapsed_seconds += duration
        return ts

    def _roll_point_winner(self, server_is_player):
        p_win = self.p_win_own_serve if server_is_player else self.p_win_on_return
        return self.rng.random() < p_win  # True => local player wins the point

    def simulate(self, match_score):
        MatchSet = self.models.MatchSet
        MatchGame = self.models.MatchGame

        sets_p1 = 0
        sets_p2 = 0
        total_duration = 0
        guest_is_serving_next_game = False  # local player serves game 1

        while True:
            current_set = MatchSet.objects.create(id_match_score=match_score, duration=0)
            set_duration, set_winner_is_player, guest_is_serving_next_game = self._simulate_set(
                current_set, guest_is_serving_next_game
            )
            current_set.duration = set_duration
            current_set.winner_id = self.player if set_winner_is_player else None
            current_set.save()

            total_duration += set_duration
            if set_winner_is_player:
                sets_p1 += 1
            else:
                sets_p2 += 1

            match_over, p1_wins = is_match_over(sets_p1, sets_p2, self.best_of)
            if match_over:
                self._backdate_points()
                return total_duration, p1_wins

    def _simulate_set(self, current_set, guest_is_serving_next_game):
        MatchGame = self.models.MatchGame

        games_p1 = 0
        games_p2 = 0
        set_duration = 0

        while True:
            over, p1_wins_set, tiebreak_needed = is_set_over(games_p1, games_p2)
            if over:
                current_set.score_p1 = games_p1
                current_set.score_p2 = games_p2
                return set_duration, p1_wins_set, guest_is_serving_next_game
            if tiebreak_needed:
                game = MatchGame.objects.create(
                    id_set=current_set, is_serving=self.player,
                    guest_is_serving=guest_is_serving_next_game, is_tiebreak=True,
                )
                game_duration, winner_is_player = self._simulate_tiebreak_game(game, guest_is_serving_next_game)
                guest_is_serving_next_game = not guest_is_serving_next_game
                set_duration += game_duration
                if winner_is_player:
                    games_p1 += 1
                else:
                    games_p2 += 1
                game.p1_game_final_score = games_p1
                game.p2_game_final_score = games_p2
                game.save(update_fields=['p1_game_final_score', 'p2_game_final_score'])
                continue

            game = MatchGame.objects.create(
                id_set=current_set, is_serving=self.player,
                guest_is_serving=guest_is_serving_next_game, is_tiebreak=False,
            )
            game_duration, winner_is_player = self._simulate_regular_game(game, guest_is_serving_next_game)
            guest_is_serving_next_game = not guest_is_serving_next_game
            set_duration += game_duration
            if winner_is_player:
                games_p1 += 1
            else:
                games_p2 += 1
            game.p1_game_final_score = games_p1
            game.p2_game_final_score = games_p2
            game.save(update_fields=['p1_game_final_score', 'p2_game_final_score'])

    def _simulate_regular_game(self, game, guest_is_serving):
        MatchPoint = self.models.MatchPoint

        server_is_player = not guest_is_serving
        score_p1 = '0'
        score_p2 = '0'
        game_duration = 0

        while True:
            player_wins_point = self._roll_point_winner(server_is_player)
            duration = _point_duration(self.rng, self.surface)
            game_duration += duration

            if player_wins_point:
                new_p1, new_p2, game_over = advance_score(score_p1, score_p2)
            else:
                new_p2, new_p1, game_over = advance_score(score_p2, score_p1)

            score_server = score_p1 if server_is_player else score_p2
            score_receiver = score_p2 if server_is_player else score_p1
            receiver_won = (player_wins_point != server_is_player)

            bp_chance = is_break_point_chance(score_server, score_receiver)
            bp = is_break_point(score_server, score_receiver, receiver_won)

            winner = self.player if player_wins_point else None
            point = MatchPoint(
                id_game=game,
                is_serving=self.player,
                id_player_1=self.player,
                id_player_2=None,
                winner_id=winner,
                score_p1=new_p1,
                score_p2=new_p2,
                duration=duration,
                break_point_chance=bp_chance,
                break_point=bp,
            )
            self._all_points.append((point, duration))

            score_p1, score_p2 = new_p1, new_p2

            if game_over:
                game.winner_id = self.player if player_wins_point else None
                game.duration = game_duration
                game.is_break = (guest_is_serving == player_wins_point)
                game.save()
                return game_duration, player_wins_point

    def _simulate_tiebreak_game(self, game, guest_is_serving):
        MatchPoint = self.models.MatchPoint

        score_p1 = '0'
        score_p2 = '0'
        game_duration = 0
        point_index = 0
        server_is_player = not guest_is_serving

        while True:
            # Tiebreak server alternates every 2 points after the first (production
            # convention via get_tiebreak_server); the win-probability split follows
            # whichever side is serving this particular point.
            current_server_is_player = (
                server_is_player if point_index == 0
                else (not server_is_player if ((point_index - 1) // 2) % 2 == 0 else server_is_player)
            )

            player_wins_point = self._roll_point_winner(current_server_is_player)
            duration = _point_duration(self.rng, self.surface)
            game_duration += duration

            if player_wins_point:
                new_p1, new_p2, game_over = advance_tiebreak_score(score_p1, score_p2)
            else:
                new_p2, new_p1, game_over = advance_tiebreak_score(score_p2, score_p1)

            winner = self.player if player_wins_point else None
            point = MatchPoint(
                id_game=game,
                is_serving=self.player,
                id_player_1=self.player,
                id_player_2=None,
                winner_id=winner,
                score_p1=new_p1,
                score_p2=new_p2,
                duration=duration,
                break_point_chance=False,
                break_point=False,
            )
            self._all_points.append((point, duration))

            score_p1, score_p2 = new_p1, new_p2
            point_index += 1

            if game_over:
                game.winner_id = self.player if player_wins_point else None
                game.duration = game_duration
                game.is_break = None
                game.save()
                return game_duration, player_wins_point

    def _backdate_points(self):
        """Persist points then fix created_at (auto_now_add bypass).

        MatchPoint.created_at is auto_now_add=True, so Django forces
        timezone.now() on INSERT regardless of what's passed to bulk_create.
        bulk_create the rows first, then bulk_update created_at with a plain
        SQL UPDATE — bulk_update does not re-trigger auto_now_add.
        """
        MatchPoint = self.models.MatchPoint

        points = [p for p, _duration in self._all_points]
        durations = [d for _p, d in self._all_points]

        MatchPoint.objects.bulk_create(points)

        elapsed = 0
        for point, duration in zip(points, durations):
            point.created_at = self.scheduled_at + timedelta(seconds=elapsed)
            elapsed += duration

        MatchPoint.objects.bulk_update(points, ['created_at'])
