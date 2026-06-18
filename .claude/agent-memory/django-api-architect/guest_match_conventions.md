---
name: guest-match-conventions
description: How matches/views.py encodes guest (player-vs-unregistered-opponent) matches across MatchGame/MatchPoint
metadata:
  type: project
---

Discovered while building `seed_demo` (see [[project-seed-demo]]), reading `matches/views.py` StartMatchView/RegisterPointView/FinishMatchView (~lines 122-270, 413-620). These conventions are load-bearing for ANY code that creates or simulates guest matches (`id_invited_player=None` on `MatchData`):

- `MatchGame.is_serving` and `MatchPoint.is_serving` are ALWAYS the registered local player — a guest has no `Usuario` row to point a FK at.
- Real server identity for guest matches is tracked separately via `MatchGame.guest_is_serving` (bool, nullable for non-guest matches).
- `guest_is_serving` toggles every new game, starting `False` (local player serves game 1).
- `server_is_creator = not current_game.guest_is_serving` — this is how production derives "is the local player currently serving" for break-point logic.
- `current_game.is_break = (current_game.guest_is_serving == winner_is_creator)` for guest-match game closure.
- `MatchPoint.id_player_2` is always `None` for guest matches.
- `winner_id` on `MatchPoint`/`MatchGame`/`MatchSet`/`MatchScore` is the player's `Usuario` if they won, `None` if the guest won (these FKs are nullable specifically for this case).
- Tiebreak points always have `break_point_chance=False`, `break_point=False` regardless of guest/non-guest.

**How to apply**: any new feature touching match creation/simulation/scoring for guest matches must mirror this exactly, not invent a parallel representation (e.g. don't try to model the guest as a second `Usuario` or a separate "is_guest" flag on points — the FK-nullability + `guest_is_serving` toggle is the established pattern).
