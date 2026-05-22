SCORE_SEQUENCE = ['0', '15', '30', '40']


def advance_score(score_winner, score_loser):
    """
    Dado el score actual del ganador y perdedor del punto,
    devuelve (nuevo_score_ganador, nuevo_score_perdedor, game_over).
    """
    if score_winner == 'AD':
        return 'AD', score_loser, True

    if score_loser == 'AD':
        return '40', '40', False

    if score_winner == '40':
        if score_loser == '40':
            return 'AD', '40', False
        return '40', score_loser, True

    idx = SCORE_SEQUENCE.index(score_winner)
    return SCORE_SEQUENCE[idx + 1], score_loser, False


def is_break_point_chance(score_server, score_receiver):
    if score_receiver == 'AD':
        return True
    if score_receiver == '40' and score_server in ('0', '15', '30'):
        return True
    return False


def is_break_point(score_server, score_receiver, receiver_won):
    return is_break_point_chance(score_server, score_receiver) and receiver_won


def is_set_over(games_p1, games_p2):
    """
    Devuelve (over, p1_wins, tiebreak_needed).
    7-6 = set ganado por tiebreak. 6-6 = tiebreak requerido.
    """
    if (games_p1 == 7 and games_p2 == 6) or (games_p2 == 7 and games_p1 == 6):
        return True, games_p1 == 7, False

    if games_p1 == 6 and games_p2 == 6:
        return False, None, True

    if games_p1 >= 6 and games_p1 - games_p2 >= 2:
        return True, True, False

    if games_p2 >= 6 and games_p2 - games_p1 >= 2:
        return True, False, False

    return False, None, False


def advance_tiebreak_score(score_winner, score_loser):
    """
    Puntuación numérica del tiebreak. Primero en llegar a 7 con 2+ de ventaja.
    Devuelve (nuevo_score_ganador, nuevo_score_perdedor, game_over).
    """
    new_winner = str(int(score_winner) + 1)
    if int(new_winner) >= 7 and int(new_winner) - int(score_loser) >= 2:
        return new_winner, score_loser, True
    return new_winner, score_loser, False


def get_tiebreak_server(initial_server_id, other_server_id, point_index):
    """
    Devuelve quién sirve en el punto de índice point_index (base 0).
    Regla: servidor inicial sirve el punto 0, luego alterna cada 2.
    Secuencia: A, B, B, A, A, B, B, A, A, ...
    """
    if point_index == 0:
        return initial_server_id
    if ((point_index - 1) // 2) % 2 == 0:
        return other_server_id
    return initial_server_id


def is_match_over(sets_p1, sets_p2, best_of):
    """Devuelve (over, p1_wins)."""
    needed = (best_of + 1) // 2
    if sets_p1 >= needed:
        return True, True
    if sets_p2 >= needed:
        return True, False
    return False, None


def get_next_server(current_server_id, creator_id, invited_id):
    return invited_id if current_server_id == creator_id else creator_id
