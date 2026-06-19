"""Pure unit tests for statistics/calculators.py — no database required."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from statistics.calculators import (
    _fmt_mmss,
    _fmt_hhmmss,
    _point_distance,
    calc_match_duration,
    calc_points_win_loss,
    calc_avg_duration_won,
    calc_avg_duration_lost,
    calc_break_points,
    calc_quartiles,
    calc_total_distance,
    calc_points_per_interval,
    calc_distance_per_interval,
    get_match_stats,
    get_live_stats,
    get_live_stats_guest,
)

PLAYER_ID = 1
OPPONENT_ID = 2
T0 = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


# ── Factories ────────────────────────────────────────────────────────────────

def make_point(
    *,
    won=True,
    duration=10,
    serving=PLAYER_ID,
    break_chance=False,
    is_guest=False,
    guest_serving=False,
    dt=T0,
):
    return SimpleNamespace(
        winner_id_id=PLAYER_ID if won else OPPONENT_ID,
        id_player_2_id=None if is_guest else OPPONENT_ID,
        duration=duration,
        is_serving_id=serving,
        break_point_chance=break_chance,
        id_game=SimpleNamespace(guest_is_serving=guest_serving),
        created_at=dt,
    )


def make_score(*, duration=3600):
    return SimpleNamespace(duration=duration, winner_id_id=PLAYER_ID)


def _to_seconds(mmss: str) -> int:
    m, s = mmss.split(":")
    return int(m) * 60 + int(s)


# ── Formatters ───────────────────────────────────────────────────────────────

class TestFmtMmss:
    def test_zero(self):
        assert _fmt_mmss(0) == "00:00"

    def test_one_minute(self):
        assert _fmt_mmss(60) == "01:00"

    def test_ninety_seconds(self):
        assert _fmt_mmss(90) == "01:30"

    def test_large(self):
        assert _fmt_mmss(3599) == "59:59"


class TestFmtHhmmss:
    def test_zero(self):
        assert _fmt_hhmmss(0) == "00:00:00"

    def test_one_hour(self):
        assert _fmt_hhmmss(3600) == "01:00:00"

    def test_mixed(self):
        assert _fmt_hhmmss(3661) == "01:01:01"


# ── Match duration ───────────────────────────────────────────────────────────

class TestCalcMatchDuration:
    def test_none_duration_returns_none(self):
        assert calc_match_duration(SimpleNamespace(duration=None)) is None

    def test_formats_correctly(self):
        assert calc_match_duration(SimpleNamespace(duration=3661)) == "01:01:01"


# ── Point distance formula ────────────────────────────────────────────────────

class TestPointDistance:
    def test_amateur_clay_male(self):
        # mpm=28.5, 60s → 60 * (28.5/60) = 28.5m
        assert abs(_point_distance(60, 'Amateur', 'Masculino', 'Clay') - 28.5) < 0.01

    def test_amateur_clay_female(self):
        # mpm=25.0, 60s → 60 * (25.0/60) = 25.0m
        assert abs(_point_distance(60, 'Amateur', 'Femenino', 'Clay') - 25.0) < 0.01

    def test_zero_duration_is_zero(self):
        assert _point_distance(0, 'Amateur', 'Masculino', 'Clay') == 0.0

    def test_unknown_combo_uses_fallback_mpm_30(self):
        # Fallback: {'effective': 20.0, 'mpm': 30.0} → 60 * (30/60) = 30.0m
        result = _point_distance(60, 'Unknown', 'Unknown', 'Unknown')
        assert abs(result - 30.0) < 0.01


# ── Points win/loss ───────────────────────────────────────────────────────────

class TestCalcPointsWinLoss:
    def test_empty_returns_zeros_without_division_error(self):
        result = calc_points_win_loss([], PLAYER_ID)
        assert result == {'won': 0, 'lost': 0, 'total': 0, 'won_pct': 0.0, 'lost_pct': 0.0}

    def test_all_won(self):
        result = calc_points_win_loss([make_point(won=True)] * 4, PLAYER_ID)
        assert result['won'] == 4
        assert result['lost'] == 0
        assert result['won_pct'] == 100.0

    def test_all_lost(self):
        result = calc_points_win_loss([make_point(won=False)] * 3, PLAYER_ID)
        assert result['won'] == 0
        assert result['won_pct'] == 0.0

    def test_mixed_counts_and_percentages(self):
        points = [make_point(won=True), make_point(won=False), make_point(won=True)]
        result = calc_points_win_loss(points, PLAYER_ID)
        assert result['won'] == 2
        assert result['lost'] == 1
        assert result['total'] == 3
        assert result['won_pct'] == round(2 / 3 * 100, 1)

    def test_adding_won_point_increases_won_pct(self):
        base = [make_point(won=True), make_point(won=False)]
        before = calc_points_win_loss(base, PLAYER_ID)['won_pct']
        after = calc_points_win_loss(base + [make_point(won=True)], PLAYER_ID)['won_pct']
        assert after > before

    def test_adding_lost_point_decreases_won_pct(self):
        base = [make_point(won=True), make_point(won=True)]
        before = calc_points_win_loss(base, PLAYER_ID)['won_pct']
        after = calc_points_win_loss(base + [make_point(won=False)], PLAYER_ID)['won_pct']
        assert after < before


# ── Average duration — won ────────────────────────────────────────────────────

class TestCalcAvgDurationWon:
    def test_empty_returns_none(self):
        assert calc_avg_duration_won([], PLAYER_ID) is None

    def test_only_lost_points_returns_none(self):
        assert calc_avg_duration_won([make_point(won=False, duration=30)], PLAYER_ID) is None

    def test_average_of_won_durations(self):
        # (30 + 90) // 2 = 60s → "01:00"
        points = [make_point(won=True, duration=30), make_point(won=True, duration=90)]
        assert calc_avg_duration_won(points, PLAYER_ID) == "01:00"

    def test_lost_points_excluded_from_average(self):
        points = [make_point(won=True, duration=30), make_point(won=False, duration=999)]
        assert calc_avg_duration_won(points, PLAYER_ID) == "00:30"

    def test_adding_longer_won_point_increases_average(self):
        base = [make_point(won=True, duration=10)]
        before = _to_seconds(calc_avg_duration_won(base, PLAYER_ID))
        after = _to_seconds(
            calc_avg_duration_won(base + [make_point(won=True, duration=90)], PLAYER_ID)
        )
        assert after > before


# ── Average duration — lost ───────────────────────────────────────────────────

class TestCalcAvgDurationLost:
    def test_empty_returns_none(self):
        assert calc_avg_duration_lost([], PLAYER_ID) is None

    def test_only_won_points_returns_none(self):
        assert calc_avg_duration_lost([make_point(won=True, duration=30)], PLAYER_ID) is None

    def test_average_of_lost_durations(self):
        # (40 + 80) // 2 = 60s → "01:00"
        points = [make_point(won=False, duration=40), make_point(won=False, duration=80)]
        assert calc_avg_duration_lost(points, PLAYER_ID) == "01:00"

    def test_won_points_excluded_from_average(self):
        points = [make_point(won=False, duration=30), make_point(won=True, duration=999)]
        assert calc_avg_duration_lost(points, PLAYER_ID) == "00:30"


# ── Break points ──────────────────────────────────────────────────────────────

class TestCalcBreakPoints:
    def test_empty_returns_zeros_without_division_error(self):
        result = calc_break_points([], PLAYER_ID)
        assert result == {
            'generated': 0, 'converted': 0, 'conversion_pct': 0.0,
            'faced': 0, 'saved': 0, 'save_pct': 0.0,
        }

    def test_no_break_chances_no_division_error(self):
        points = [make_point(break_chance=False), make_point(won=False, break_chance=False)]
        result = calc_break_points(points, PLAYER_ID)
        assert result['conversion_pct'] == 0.0
        assert result['save_pct'] == 0.0

    def test_generated_and_converted(self):
        # OPPONENT serves → PLAYER can generate break points
        won_bp = make_point(won=True,  serving=OPPONENT_ID, break_chance=True)
        lost_bp = make_point(won=False, serving=OPPONENT_ID, break_chance=True)
        result = calc_break_points([won_bp, lost_bp], PLAYER_ID)
        assert result['generated'] == 2
        assert result['converted'] == 1
        assert result['conversion_pct'] == 50.0

    def test_faced_and_saved(self):
        # PLAYER serves → PLAYER faces break points
        saved = make_point(won=True,  serving=PLAYER_ID, break_chance=True)
        lost  = make_point(won=False, serving=PLAYER_ID, break_chance=True)
        result = calc_break_points([saved, lost], PLAYER_ID)
        assert result['faced'] == 2
        assert result['saved'] == 1
        assert result['save_pct'] == 50.0

    def test_no_generated_break_points_no_conversion_pct_error(self):
        # PLAYER only serves — no BPs generated — should not raise ZeroDivisionError
        result = calc_break_points(
            [make_point(won=True, serving=PLAYER_ID, break_chance=True)], PLAYER_ID
        )
        assert result['generated'] == 0
        assert result['conversion_pct'] == 0.0

    def test_no_faced_break_points_no_save_pct_error(self):
        # OPPONENT only serves — no BPs faced — should not raise ZeroDivisionError
        result = calc_break_points(
            [make_point(won=True, serving=OPPONENT_ID, break_chance=True)], PLAYER_ID
        )
        assert result['faced'] == 0
        assert result['save_pct'] == 0.0

    def test_100_pct_conversion(self):
        points = [make_point(won=True, serving=OPPONENT_ID, break_chance=True)] * 3
        assert calc_break_points(points, PLAYER_ID)['conversion_pct'] == 100.0

    def test_100_pct_save(self):
        points = [make_point(won=True, serving=PLAYER_ID, break_chance=True)] * 3
        assert calc_break_points(points, PLAYER_ID)['save_pct'] == 100.0


# ── Quartiles ─────────────────────────────────────────────────────────────────

class TestCalcQuartiles:
    def test_empty_returns_empty_list(self):
        assert calc_quartiles([]) == []

    def test_always_returns_four_buckets(self):
        assert len(calc_quartiles([make_point(duration=10)])) == 4

    def test_colors_in_order(self):
        result = calc_quartiles([make_point(duration=i) for i in range(1, 9)])
        assert [q['color'] for q in result] == ['green', 'yellow', 'orange', 'red']

    def test_percentages_sum_to_100(self):
        result = calc_quartiles([make_point(duration=i) for i in range(1, 9)])
        assert abs(sum(q['pct'] for q in result) - 100.0) < 0.1

    def test_counts_sum_to_total_points(self):
        points = [make_point(duration=i) for i in range(1, 13)]
        result = calc_quartiles(points)
        assert sum(q['count'] for q in result) == 12

    def test_min_duration_boundaries_are_non_decreasing(self):
        result = calc_quartiles([make_point(duration=d) for d in [2, 8, 5, 12, 1, 20]])
        mins = [q['min_duration'] for q in result]
        assert mins == sorted(mins)


# ── Total distance ────────────────────────────────────────────────────────────

class TestCalcTotalDistance:
    def test_empty_is_zero(self):
        assert calc_total_distance([], 'Amateur', 'Masculino', 'Clay') == 0.0

    def test_single_point_formula_amateur_clay_male(self):
        # 60s * (28.5/60) = 28.5m
        result = calc_total_distance([make_point(duration=60)], 'Amateur', 'Masculino', 'Clay')
        assert abs(result - 28.5) < 0.01

    def test_two_equal_points_double_the_distance(self):
        one = calc_total_distance([make_point(duration=60)], 'Amateur', 'Masculino', 'Clay')
        two = calc_total_distance([make_point(duration=60)] * 2, 'Amateur', 'Masculino', 'Clay')
        assert abs(two - one * 2) < 0.01

    def test_adding_point_increases_total(self):
        base = [make_point(duration=30)]
        before = calc_total_distance(base, 'Amateur', 'Masculino', 'Clay')
        after = calc_total_distance(base + [make_point(duration=30)], 'Amateur', 'Masculino', 'Clay')
        assert after > before

    def test_longer_point_means_more_distance(self):
        short = calc_total_distance([make_point(duration=30)], 'Amateur', 'Masculino', 'Clay')
        long_ = calc_total_distance([make_point(duration=90)], 'Amateur', 'Masculino', 'Clay')
        assert long_ > short


# ── Points per interval ───────────────────────────────────────────────────────

class TestCalcPointsPerInterval:
    def test_empty_returns_empty_list(self):
        assert calc_points_per_interval([], PLAYER_ID) == []

    def test_all_in_first_interval(self):
        points = [
            make_point(won=True, dt=T0),
            make_point(won=True, dt=T0 + timedelta(seconds=60)),
            make_point(won=True, dt=T0 + timedelta(seconds=240)),
        ]
        assert calc_points_per_interval(points, PLAYER_ID) == [{'interval': 5, 'points_won': 3}]

    def test_only_won_points_counted(self):
        points = [
            make_point(won=True, dt=T0),
            make_point(won=False, dt=T0 + timedelta(seconds=30)),
        ]
        assert calc_points_per_interval(points, PLAYER_ID) == [{'interval': 5, 'points_won': 1}]

    def test_only_lost_points_returns_empty(self):
        points = [make_point(won=False, dt=T0), make_point(won=False, dt=T0 + timedelta(seconds=10))]
        assert calc_points_per_interval(points, PLAYER_ID) == []

    def test_spans_two_intervals(self):
        points = [
            make_point(won=True, dt=T0),
            make_point(won=True, dt=T0 + timedelta(seconds=301)),
        ]
        result = calc_points_per_interval(points, PLAYER_ID)
        intervals = {r['interval'] for r in result}
        assert 5 in intervals
        assert 10 in intervals

    def test_adding_won_point_increments_interval_count(self):
        base = [make_point(won=True, dt=T0)]
        before = calc_points_per_interval(base, PLAYER_ID)[0]['points_won']
        after = calc_points_per_interval(
            base + [make_point(won=True, dt=T0 + timedelta(seconds=30))], PLAYER_ID
        )
        assert after[0]['points_won'] == before + 1


# ── Distance per interval ─────────────────────────────────────────────────────

class TestCalcDistancePerInterval:
    def test_empty_returns_empty_list(self):
        assert calc_distance_per_interval([], 'Amateur', 'Masculino', 'Clay') == []

    def test_single_point_correct_interval_and_distance(self):
        result = calc_distance_per_interval(
            [make_point(duration=60, dt=T0)], 'Amateur', 'Masculino', 'Clay'
        )
        assert len(result) == 1
        assert result[0]['interval'] == 5
        assert abs(result[0]['distance'] - 28.5) < 0.01

    def test_adding_point_to_same_interval_increases_distance(self):
        base = [make_point(duration=60, dt=T0)]
        before = calc_distance_per_interval(base, 'Amateur', 'Masculino', 'Clay')[0]['distance']
        after = calc_distance_per_interval(
            base + [make_point(duration=60, dt=T0 + timedelta(seconds=30))],
            'Amateur', 'Masculino', 'Clay',
        )
        assert after[0]['distance'] > before

    def test_spans_two_intervals(self):
        points = [
            make_point(duration=30, dt=T0),
            make_point(duration=30, dt=T0 + timedelta(seconds=301)),
        ]
        result = calc_distance_per_interval(points, 'Amateur', 'Masculino', 'Clay')
        assert len(result) == 2


# ── get_match_stats (composite) ───────────────────────────────────────────────

class TestGetMatchStats:
    def test_empty_points_returns_complete_structure(self):
        result = get_match_stats([], PLAYER_ID, make_score(), 'Amateur', 'Masculino', 'Clay')
        assert set(result.keys()) == {
            'match_duration', 'points_win_loss', 'avg_duration_won',
            'avg_duration_lost', 'break_points', 'total_distance',
            'quartiles', 'points_per_interval', 'distance_per_interval',
        }
        assert result['avg_duration_won'] is None
        assert result['avg_duration_lost'] is None
        assert result['quartiles'] == []
        assert result['points_per_interval'] == []

    def test_with_points_populates_numeric_fields(self):
        points = [make_point(won=True, duration=30), make_point(won=False, duration=20)]
        result = get_match_stats(points, PLAYER_ID, make_score(), 'Amateur', 'Masculino', 'Clay')
        assert result['points_win_loss']['total'] == 2
        assert result['total_distance'] > 0
        assert result['avg_duration_won'] is not None
        assert result['avg_duration_lost'] is not None
        assert len(result['quartiles']) == 4


# ── get_live_stats ────────────────────────────────────────────────────────────

class TestGetLiveStats:
    def test_empty_no_errors(self):
        result = get_live_stats([], PLAYER_ID, 'Amateur', 'Masculino', 'Clay')
        assert set(result.keys()) == {
            'points_win_loss', 'avg_duration_won', 'avg_duration_lost',
            'break_points', 'total_distance',
        }
        assert result['avg_duration_won'] is None
        assert result['total_distance'] == 0.0

    def test_with_points_populates_fields(self):
        points = [make_point(won=True, duration=30), make_point(won=False, duration=20)]
        result = get_live_stats(points, PLAYER_ID, 'Amateur', 'Masculino', 'Clay')
        assert result['points_win_loss']['total'] == 2
        assert result['total_distance'] > 0


# ── get_live_stats_guest ──────────────────────────────────────────────────────

class TestGetLiveStatsGuest:
    def test_empty_returns_safe_defaults(self):
        result = get_live_stats_guest([], PLAYER_ID)
        assert result['total_distance'] is None
        assert result['points_win_loss']['total'] == 0
        assert result['points_win_loss']['won_pct'] == 0.0

    def test_total_distance_always_none(self):
        result = get_live_stats_guest([make_point(duration=60, is_guest=True)], PLAYER_ID)
        assert result['total_distance'] is None

    def test_win_loss_is_mirror_of_local(self):
        # PLAYER won 2, lost 1 → guest won 1, lost 2
        points = [
            make_point(won=True,  is_guest=True),
            make_point(won=True,  is_guest=True),
            make_point(won=False, is_guest=True),
        ]
        result = get_live_stats_guest(points, PLAYER_ID)
        assert result['points_win_loss']['won'] == 1
        assert result['points_win_loss']['lost'] == 2

    def test_avg_duration_won_reflects_guest_perspective(self):
        # Guest wins on points PLAYER lost (won=False from PLAYER perspective)
        points = [
            make_point(won=False, duration=40, is_guest=True),
            make_point(won=False, duration=80, is_guest=True),
            make_point(won=True,  duration=10, is_guest=True),  # local win — not in guest avg_won
        ]
        result = get_live_stats_guest(points, PLAYER_ID)
        # guest avg won: (40 + 80) // 2 = 60s → "01:00"
        assert result['avg_duration_won'] == "01:00"


# ── get_global_stats (mocked DB) ──────────────────────────────────────────────

def _make_match(match_id, surface='Clay', winner_id=PLAYER_ID, local_id=PLAYER_ID,
                invited=None, guest_name=None, points=None):
    score = SimpleNamespace(winner_id_id=winner_id, duration=3600)
    match = SimpleNamespace(
        id_match=match_id,
        surface=surface,
        location='Test Court',
        match_score=score,
        id_local_player=SimpleNamespace(id=local_id, nombre='Test', apellidoPaterno='Player'),
        id_local_player_id=local_id,
        id_invited_player=invited,
        guest_name=guest_name,
    )
    return match, (points or [])


def _run_global_stats(matches, points_by_match):
    import sys
    from statistics.calculators import get_global_stats

    all_points = []
    for match, pts in zip(matches, points_by_match):
        for p in pts:
            p.id_game = SimpleNamespace(
                id_set=SimpleNamespace(
                    id_match_score=SimpleNamespace(id_partido_id=match.id_match)
                ),
                guest_is_serving=False,
            )
        all_points.extend(pts)

    mock_mp = MagicMock()
    mock_mp.objects.filter.return_value.select_related.return_value.order_by.return_value = iter(all_points)

    fake_matches_models = MagicMock()
    fake_matches_models.MatchPoint = mock_mp

    # Inject the fake module so the local import inside get_global_stats resolves it
    with patch.dict(sys.modules, {'matches': MagicMock(), 'matches.models': fake_matches_models}):
        return get_global_stats(matches, PLAYER_ID, 'Amateur', 'Masculino')


class TestGetGlobalStats:
    def test_no_matches_no_points_returns_safe_structure(self):
        result = _run_global_stats([], [])
        assert result['record'] == {'wins': 0, 'losses': 0, 'total': 0, 'win_pct': 0.0, 'loss_pct': 0.0}
        assert result['last_result'] is None
        assert result['total_distance'] == 0.0
        assert result['quartiles'] == []

    def test_single_won_match_record(self):
        match, pts = _make_match(match_id=1, winner_id=PLAYER_ID)
        result = _run_global_stats([match], [pts])
        assert result['record']['wins'] == 1
        assert result['record']['losses'] == 0
        assert result['record']['win_pct'] == 100.0

    def test_single_lost_match_record(self):
        match, pts = _make_match(match_id=1, winner_id=OPPONENT_ID)
        result = _run_global_stats([match], [pts])
        assert result['record']['wins'] == 0
        assert result['record']['losses'] == 1

    def test_last_result_is_most_recent_match(self):
        match, pts = _make_match(match_id=1, winner_id=PLAYER_ID)
        invited = SimpleNamespace(id=OPPONENT_ID, nombre='Rival', apellidoPaterno='Test')
        match.id_invited_player = invited
        result = _run_global_stats([match], [pts])
        assert result['last_result']['won'] is True
        assert result['last_result']['opponent']['nombre'] == 'Rival'

    def test_points_contribute_to_distance(self):
        match, _ = _make_match(match_id=1)
        pts = [make_point(duration=60), make_point(duration=60)]
        result = _run_global_stats([match], [pts])
        # 2 * 60 * (28.5/60) = 57.0m
        assert abs(result['total_distance'] - 57.0) < 0.01

    def test_win_loss_aggregates_across_points(self):
        match, _ = _make_match(match_id=1)
        pts = [make_point(won=True), make_point(won=False), make_point(won=True)]
        result = _run_global_stats([match], [pts])
        assert result['points_win_loss']['won'] == 2
        assert result['points_win_loss']['lost'] == 1

    def test_no_points_avg_duration_returns_none(self):
        match, pts = _make_match(match_id=1)
        result = _run_global_stats([match], [pts])
        assert result['avg_duration_won'] is None
        assert result['avg_duration_lost'] is None
