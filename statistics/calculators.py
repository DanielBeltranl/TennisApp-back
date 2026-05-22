from collections import defaultdict
from django.conf import settings


def _distance_params(nivel, sexo, surface):
    key = (nivel, surface, sexo)
    params = settings.TENNIS_DISTANCE_PARAMS
    if key not in params:
        key = (nivel, surface, 'Masculino')
    return params.get(key, {'effective': 20.0, 'mpm': 30.0})


def _point_distance(duration_seconds, nivel, sexo, surface):
    p = _distance_params(nivel, sexo, surface)
    return duration_seconds * (p['effective'] / 100) * (p['mpm'] / 60)


def _fmt_mmss(seconds):
    return f"{int(seconds) // 60:02d}:{int(seconds) % 60:02d}"


def _fmt_hhmmss(seconds):
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ── métricas individuales ────────────────────────────────────────────────────

def calc_match_duration(match_score):
    if match_score.duration is None:
        return None
    return _fmt_hhmmss(match_score.duration)


def calc_points_win_loss(points, player_id):
    total = len(points)
    won = sum(1 for p in points if p.winner_id_id == player_id)
    lost = total - won
    return {
        'won': won,
        'lost': lost,
        'total': total,
        'won_pct': round(won / total * 100, 1) if total else 0.0,
        'lost_pct': round(lost / total * 100, 1) if total else 0.0,
    }


def calc_avg_duration_won(points, player_id):
    durations = [p.duration for p in points if p.winner_id_id == player_id]
    if not durations:
        return None
    return _fmt_mmss(sum(durations) // len(durations))


def calc_avg_duration_lost(points, player_id):
    durations = [p.duration for p in points if p.winner_id_id != player_id]
    if not durations:
        return None
    return _fmt_mmss(sum(durations) // len(durations))


def calc_break_points(points, player_id):
    generated = [p for p in points if p.is_serving_id != player_id and p.break_point_chance]
    converted = [p for p in generated if p.winner_id_id == player_id]
    faced     = [p for p in points if p.is_serving_id == player_id and p.break_point_chance]
    saved     = [p for p in faced if p.winner_id_id == player_id]

    gen   = len(generated)
    fcd   = len(faced)
    conv  = len(converted)
    sav   = len(saved)

    return {
        'generated':      gen,
        'converted':      conv,
        'conversion_pct': round(conv / gen * 100, 1) if gen else 0.0,
        'faced':          fcd,
        'saved':          sav,
        'save_pct':       round(sav / fcd * 100, 1) if fcd else 0.0,
    }


def calc_quartiles(points):
    if not points:
        return []

    durations = sorted(p.duration for p in points)
    total = len(durations)

    def pct_idx(pct):
        return min(int(pct / 100 * total), total - 1)

    q1 = durations[pct_idx(25)]
    q2 = durations[pct_idx(50)]
    q3 = durations[pct_idx(75)]

    def classify(d):
        if d <= q1: return 1
        if d <= q2: return 2
        if d <= q3: return 3
        return 4

    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for d in durations:
        counts[classify(d)] += 1

    meta = {
        1: ('green',  durations[0], q1),
        2: ('yellow', q1,           q2),
        3: ('orange', q2,           q3),
        4: ('red',    q3,           durations[-1]),
    }

    return [
        {
            'quartile':     i,
            'color':        meta[i][0],
            'min_duration': meta[i][1],
            'max_duration': meta[i][2],
            'count':        counts[i],
            'pct':          round(counts[i] / total * 100, 1),
        }
        for i in range(1, 5)
    ]


def calc_total_distance(points, nivel, sexo, surface):
    return round(sum(_point_distance(p.duration, nivel, sexo, surface) for p in points), 2)


def calc_points_per_interval(points, player_id):
    if not points:
        return []

    match_start = points[0].created_at
    buckets = defaultdict(int)

    for p in points:
        if p.winner_id_id != player_id:
            continue
        elapsed  = (p.created_at - match_start).total_seconds()
        interval = (int(elapsed) // 300 + 1) * 5
        buckets[interval] += 1

    return [{'interval': k, 'points_won': v} for k, v in sorted(buckets.items())]


def calc_distance_per_interval(points, nivel, sexo, surface):
    if not points:
        return []

    match_start = points[0].created_at
    buckets = defaultdict(float)

    for p in points:
        elapsed  = (p.created_at - match_start).total_seconds()
        interval = (int(elapsed) // 300 + 1) * 5
        buckets[interval] += _point_distance(p.duration, nivel, sexo, surface)

    return [{'interval': k, 'distance': round(v, 2)} for k, v in sorted(buckets.items())]


# ── agregadores para stats globales ─────────────────────────────────────────

def _record(matches, player_id):
    wins  = sum(1 for m in matches if m.match_score.winner_id_id == player_id)
    total = len(matches)
    losses = total - wins
    return {
        'wins':     wins,
        'losses':   losses,
        'total':    total,
        'win_pct':  round(wins   / total * 100, 1) if total else 0.0,
        'loss_pct': round(losses / total * 100, 1) if total else 0.0,
    }


def _last_result(matches, player_id):
    if not matches:
        return None
    last = matches[0]
    opponent = (
        last.id_player_invited if last.id_player_creator_id == player_id
        else last.id_player_creator
    )
    return {
        'match_id': str(last.id_match),
        'won':      last.match_score.winner_id_id == player_id,
        'opponent': {
            'id':              opponent.id,
            'nombre':          opponent.nombre,
            'apellidoPaterno': opponent.apellidoPaterno,
        },
        'location': last.location,
        'surface':  last.surface,
    }


def _avg_points_per_interval(points_by_match, match_starts, player_id, match_count):
    combined = defaultdict(int)

    for mid, points in points_by_match.items():
        start = match_starts.get(mid)
        if not start:
            continue
        for p in points:
            if p.winner_id_id != player_id:
                continue
            elapsed  = (p.created_at - start).total_seconds()
            interval = (int(elapsed) // 300 + 1) * 5
            combined[interval] += 1

    return [
        {'interval': k, 'points_won_avg': round(v / match_count, 2)}
        for k, v in sorted(combined.items())
    ]


def _avg_distance_per_interval(points_by_match, match_starts, match_surface, nivel, sexo, match_count):
    combined = defaultdict(float)

    for mid, points in points_by_match.items():
        start   = match_starts.get(mid)
        surface = match_surface.get(mid, 'Clay')
        if not start:
            continue
        for p in points:
            elapsed  = (p.created_at - start).total_seconds()
            interval = (int(elapsed) // 300 + 1) * 5
            combined[interval] += _point_distance(p.duration, nivel, sexo, surface)

    return [
        {'interval': k, 'distance_avg': round(v / match_count, 2)}
        for k, v in sorted(combined.items())
    ]


# ── entrypoints públicos ─────────────────────────────────────────────────────

def get_match_stats(points, player_id, match_score, nivel, sexo, surface):
    return {
        'match_duration':        calc_match_duration(match_score),
        'points_win_loss':       calc_points_win_loss(points, player_id),
        'avg_duration_won':      calc_avg_duration_won(points, player_id),
        'avg_duration_lost':     calc_avg_duration_lost(points, player_id),
        'break_points':          calc_break_points(points, player_id),
        'total_distance':        calc_total_distance(points, nivel, sexo, surface),
        'quartiles':             calc_quartiles(points),
        'points_per_interval':   calc_points_per_interval(points, player_id),
        'distance_per_interval': calc_distance_per_interval(points, nivel, sexo, surface),
    }


def get_global_stats(matches, player_id, nivel, sexo):
    match_ids    = [m.id_match for m in matches]
    match_surface = {m.id_match: m.surface for m in matches}

    from matches.models import MatchPoint
    all_points = list(
        MatchPoint.objects.filter(
            id_game__id_set__id_match_score__id_partido__in=match_ids
        )
        .select_related('winner_id', 'is_serving', 'id_game__id_set__id_match_score')
        .order_by('id_game__id_set__id_match_score__id_partido_id', 'created_at')
    )

    points_by_match = defaultdict(list)
    match_starts    = {}

    for p in all_points:
        mid = p.id_game.id_set.id_match_score.id_partido_id
        points_by_match[mid].append(p)

    for mid, pts in points_by_match.items():
        if pts:
            match_starts[mid] = pts[0].created_at

    total_dist = sum(
        calc_total_distance(pts, nivel, sexo, match_surface[mid])
        for mid, pts in points_by_match.items()
    )

    n = len(matches)

    return {
        'record':                _record(matches, player_id),
        'last_result':           _last_result(matches, player_id),
        'total_distance':        round(total_dist, 2),
        'avg_duration_won':      calc_avg_duration_won(all_points, player_id),
        'avg_duration_lost':     calc_avg_duration_lost(all_points, player_id),
        'points_win_loss':       calc_points_win_loss(all_points, player_id),
        'break_points':          calc_break_points(all_points, player_id),
        'quartiles':             calc_quartiles(all_points),
        'points_per_interval':   _avg_points_per_interval(points_by_match, match_starts, player_id, n),
        'distance_per_interval': _avg_distance_per_interval(points_by_match, match_starts, match_surface, nivel, sexo, n),
    }
