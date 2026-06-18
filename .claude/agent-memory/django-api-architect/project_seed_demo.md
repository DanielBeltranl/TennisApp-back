---
name: project-seed-demo
description: seed_demo management command — guest-match-only demo data, auto_now_add backdating workaround, idempotency gate
metadata:
  type: project
---

Built `apiusuario/management/commands/seed_demo.py` (2026-06-17) to seed demo data on every container boot: 2 coaches + 10 players (5 each, linked via `Usuario.entrenador` FK) + 1 finished guest match per player. Wired into `docker-compose.yml` web command between `migrate` and `daphne`.

**Why**: user wants populated dashboards immediately on `docker-compose up`, replacing a manually-run, now-deleted `seed_data.py` (recoverable via `git show dfc8f6d:apiusuario/management/commands/seed_data.py` if old name/data tables are needed again).

**How to apply**:
- All seeded matches are player-vs-unregistered-guest (`id_invited_player=None`), never player-vs-player — this was an explicit user decision, confirm before changing.
- `MatchPoint.created_at` is `auto_now_add=True`. To backdate timestamps for realistic interval-bucketed stats: `bulk_create()` then mutate `.created_at` in memory then `bulk_update(points, ['created_at'])` — this is the only way that bypasses auto_now_add. Any future seeding/backfill script touching `MatchPoint` needs this same pattern.
- Demo password for all 12 seeded accounts: `Tennis2024!` (real, via `set_password()` — not unusable-password marker).
- Idempotency gate checks only `Usuario.objects.filter(correo='coach.carlos@tennis.app').exists()` — if that one row exists assume the whole seed ran; don't add finer-grained checks per spec (this is additive demo data, not upsert-critical).
- Simulation reuses production scoring functions from `matches/services.py` (advance_score, advance_tiebreak_score, is_break_point_chance/is_break_point, is_set_over, is_match_over) — never hand-script scorelines for demo/test data in this project; let the match outcome emerge from per-point probability rolls so it matches what production actually generates structurally.
- See engram memory `decision/seed-demo-management-command-guest-matches-auto-now-add-backdating-shared-password` for full detail.

Related: [[guest-match-conventions]]
