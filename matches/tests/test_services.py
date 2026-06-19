"""
Pure unit tests for matches/services.py.

No database, no Django setup needed — every function here takes primitive
Python values (strings, ints, ids) and returns primitive Python values.
"""
import pytest

from matches.services import (
    advance_score,
    advance_tiebreak_score,
    get_next_server,
    get_tiebreak_server,
    is_break_point,
    is_break_point_chance,
    is_match_over,
    is_set_over,
)

CREATOR = 1
INVITED = 2


# ── advance_score ─────────────────────────────────────────────────────────────

class TestAdvanceScore:
    # Normal progression
    def test_0_to_15(self):
        assert advance_score('0', '0') == ('15', '0', False)

    def test_15_to_30(self):
        assert advance_score('15', '0') == ('30', '0', False)

    def test_30_to_40(self):
        assert advance_score('30', '0') == ('40', '0', False)

    # Game won outright (winner at 40, loser below 40)
    def test_40_vs_0_game_over(self):
        assert advance_score('40', '0') == ('40', '0', True)

    def test_40_vs_15_game_over(self):
        assert advance_score('40', '15') == ('40', '15', True)

    def test_40_vs_30_game_over(self):
        assert advance_score('40', '30') == ('40', '30', True)

    # Deuce sequences
    def test_40_vs_40_gives_advantage(self):
        assert advance_score('40', '40') == ('AD', '40', False)

    def test_ad_wins_game(self):
        assert advance_score('AD', '40') == ('AD', '40', True)

    def test_loser_ad_returns_to_deuce(self):
        # The loser had advantage (opponent won the point back from deuce)
        assert advance_score('40', 'AD') == ('40', '40', False)

    # Loser score stays unchanged on a normal advance
    def test_loser_score_unchanged_on_normal_advance(self):
        new_w, new_l, over = advance_score('15', '30')
        assert new_w == '30'
        assert new_l == '30'
        assert over is False


# ── is_break_point_chance ─────────────────────────────────────────────────────

class TestIsBreakPointChance:
    def test_receiver_at_40_server_at_0(self):
        assert is_break_point_chance('0', '40') is True

    def test_receiver_at_40_server_at_15(self):
        assert is_break_point_chance('15', '40') is True

    def test_receiver_at_40_server_at_30(self):
        assert is_break_point_chance('30', '40') is True

    def test_receiver_ad_is_break_point(self):
        assert is_break_point_chance('40', 'AD') is True

    def test_deuce_is_not_break_point(self):
        assert is_break_point_chance('40', '40') is False

    def test_server_advantage_not_break_point(self):
        assert is_break_point_chance('AD', '40') is False

    def test_receiver_at_30_not_break_point(self):
        assert is_break_point_chance('0', '30') is False

    def test_equal_scores_not_break_point(self):
        assert is_break_point_chance('15', '15') is False


# ── is_break_point ────────────────────────────────────────────────────────────

class TestIsBreakPoint:
    def test_bp_chance_and_receiver_wins(self):
        assert is_break_point('0', '40', receiver_won=True) is True

    def test_bp_chance_but_server_wins(self):
        assert is_break_point('0', '40', receiver_won=False) is False

    def test_no_bp_chance_receiver_wins(self):
        assert is_break_point('40', '0', receiver_won=True) is False

    def test_ad_receiver_wins(self):
        assert is_break_point('40', 'AD', receiver_won=True) is True


# ── is_set_over ───────────────────────────────────────────────────────────────

class TestIsSetOver:
    # Set not over yet
    def test_0_0_not_over(self):
        assert is_set_over(0, 0) == (False, None, False)

    def test_5_4_not_over(self):
        assert is_set_over(5, 4) == (False, None, False)

    def test_6_5_not_over(self):
        assert is_set_over(6, 5) == (False, None, False)

    def test_5_5_not_over(self):
        assert is_set_over(5, 5) == (False, None, False)

    # Standard wins
    def test_6_0_p1_wins(self):
        assert is_set_over(6, 0) == (True, True, False)

    def test_6_4_p1_wins(self):
        assert is_set_over(6, 4) == (True, True, False)

    def test_7_5_p1_wins(self):
        assert is_set_over(7, 5) == (True, True, False)

    def test_0_6_p2_wins(self):
        assert is_set_over(0, 6) == (True, False, False)

    def test_4_6_p2_wins(self):
        assert is_set_over(4, 6) == (True, False, False)

    def test_5_7_p2_wins(self):
        assert is_set_over(5, 7) == (True, False, False)

    # Tiebreak trigger
    def test_6_6_tiebreak_required(self):
        assert is_set_over(6, 6) == (False, None, True)

    # After tiebreak
    def test_7_6_p1_wins_tiebreak(self):
        assert is_set_over(7, 6) == (True, True, False)

    def test_6_7_p2_wins_tiebreak(self):
        assert is_set_over(6, 7) == (True, False, False)


# ── advance_tiebreak_score ────────────────────────────────────────────────────

class TestAdvanceTiebreakScore:
    def test_normal_increment(self):
        assert advance_tiebreak_score('0', '0') == ('1', '0', False)

    def test_not_over_at_6_6(self):
        # 7-6: needs 2-point lead, 1 is not enough
        assert advance_tiebreak_score('6', '6') == ('7', '6', False)

    def test_over_at_7_4(self):
        assert advance_tiebreak_score('6', '4') == ('7', '4', True)

    def test_over_at_7_0(self):
        assert advance_tiebreak_score('6', '0') == ('7', '0', True)

    def test_over_at_extended_tiebreak(self):
        # 12-10 win
        assert advance_tiebreak_score('11', '10') == ('12', '10', True)

    def test_not_over_needs_two_clear(self):
        # At 7-7 → 8-7, not enough lead
        assert advance_tiebreak_score('7', '7') == ('8', '7', False)

    def test_over_with_two_clear(self):
        # At 8-6 → 9-6, 3 difference but still >= 2 so over
        assert advance_tiebreak_score('8', '6') == ('9', '6', True)


# ── get_tiebreak_server ───────────────────────────────────────────────────────

class TestGetTiebreakServer:
    """
    Server rotation: A, B, B, A, A, B, B, A, A, ...
    Initial server (A) serves point 0, then alternates every 2 points.
    """

    def test_point_0_initial_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 0) == CREATOR

    def test_point_1_other_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 1) == INVITED

    def test_point_2_other_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 2) == INVITED

    def test_point_3_initial_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 3) == CREATOR

    def test_point_4_initial_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 4) == CREATOR

    def test_point_5_other_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 5) == INVITED

    def test_point_6_other_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 6) == INVITED

    def test_point_7_initial_server(self):
        assert get_tiebreak_server(CREATOR, INVITED, 7) == CREATOR

    def test_full_rotation_sequence(self):
        expected = [CREATOR, INVITED, INVITED, CREATOR, CREATOR, INVITED, INVITED, CREATOR]
        result = [get_tiebreak_server(CREATOR, INVITED, i) for i in range(8)]
        assert result == expected


# ── is_match_over ─────────────────────────────────────────────────────────────

class TestIsMatchOver:
    # Best-of-1 (needed: 1 set)
    def test_bo1_p1_wins(self):
        assert is_match_over(1, 0, best_of=1) == (True, True)

    def test_bo1_p2_wins(self):
        assert is_match_over(0, 1, best_of=1) == (True, False)

    def test_bo1_not_started(self):
        assert is_match_over(0, 0, best_of=1) == (False, None)

    # Best-of-3 (needed: 2 sets)
    def test_bo3_p1_wins(self):
        assert is_match_over(2, 0, best_of=3) == (True, True)

    def test_bo3_p2_wins(self):
        assert is_match_over(0, 2, best_of=3) == (True, False)

    def test_bo3_tied_not_over(self):
        assert is_match_over(1, 1, best_of=3) == (False, None)

    def test_bo3_p1_leads_not_over(self):
        assert is_match_over(1, 0, best_of=3) == (False, None)

    # Best-of-5 (needed: 3 sets)
    def test_bo5_p1_wins(self):
        assert is_match_over(3, 0, best_of=5) == (True, True)

    def test_bo5_p2_wins(self):
        assert is_match_over(0, 3, best_of=5) == (True, False)

    def test_bo5_p1_wins_3_2(self):
        assert is_match_over(3, 2, best_of=5) == (True, True)

    def test_bo5_tied_not_over(self):
        assert is_match_over(2, 2, best_of=5) == (False, None)


# ── get_next_server ───────────────────────────────────────────────────────────

class TestGetNextServer:
    def test_creator_serves_next_is_invited(self):
        assert get_next_server(CREATOR, CREATOR, INVITED) == INVITED

    def test_invited_serves_next_is_creator(self):
        assert get_next_server(INVITED, CREATOR, INVITED) == CREATOR

    def test_alternation_full_cycle(self):
        server = CREATOR
        for _ in range(4):
            server = get_next_server(server, CREATOR, INVITED)
        assert server == CREATOR
