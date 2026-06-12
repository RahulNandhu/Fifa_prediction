# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

A Django 5.2.15 app implementing the FIFA World Cup Prediction Contest described in `SPEC.md`: contest groups,
membership approvals, fixtures/matches, predictions with deadlines, automatic scoring, leaderboards, manual point
adjustments, and audit logging. User-facing pages use Django templates + Bootstrap 5 (`django-bootstrap5`);
admin-only workflows (membership approval, match publishing, result entry, point adjustments, prediction
monitoring) use the built-in Django Admin — no custom admin dashboard.

## Environment

Config is loaded from `.env` (via `python-decouple`): `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `DB_*` (Postgres
connection — local dev DB is named `fifa`). A virtualenv exists at `venv/`. Activate it before running commands:

```powershell
.\venv\Scripts\Activate.ps1
```

## Common commands

Run all commands from the repository root (`C:\AT_Projects\Fifa`), with the venv activated:

```powershell
python manage.py runserver          # start the dev server
python manage.py makemigrations     # generate migrations after model changes
python manage.py migrate            # apply migrations to Postgres
python manage.py createsuperuser    # create an admin user
python manage.py test               # run the test suite
python manage.py test <app_label>   # run tests for a single app
python manage.py shell              # interactive shell with project loaded
```

## Architecture

Four apps, each owning one slice of the domain model (see `SPEC.md` for the full spec):

- **accounts** — registration, login/logout (Django auth views), and the user dashboard. No models of its own;
  uses the built-in `User` model. `accounts/urls.py` is included at `/accounts/`.
- **contests** — `ContestGroup` and `GroupMembership` (status: Pending/Approved/Rejected). The `groups` view lets
  users request to join a group; admins approve/reject via Django Admin actions (`contests/admin.py`). Included at
  `/groups/`.
- **matches** — `Team` (national team: `name` + ISO 3166-1 alpha-2 `code`; `flag` property derives the emoji flag
  from `code`), `Fixture` (home/away `Team` FKs + kickoff time/stage/venue, created by admins via the Fixture admin
  page — `home_team`/`away_team` use `autocomplete_fields` for a searchable flag+name dropdown), and `Match` (a
  fixture an admin has published). `Outcome` (HOME/AWAY/DRAW) is defined here and shared with `predictions`.
  `Match.prediction_deadline` is derived (kickoff − `PREDICTION_DEADLINE_MINUTES_BEFORE_KICKOFF`, set in
  `config/settings.py` and currently `0`, i.e. the deadline is kickoff time itself), not stored. Included at
  `/matches/`. The 48 national teams are seeded via the
  `matches/migrations/0003_seed_teams.py` data migration — edit/add/remove teams via Django Admin (Teams) as the
  actual tournament draw is finalized.
- **predictions** — `Prediction` (per user/match scoreline; winner is derived from the scoreline via
  `predicted_winner`) and `PointTransaction` (audit trail for both auto-scored predictions and manual admin
  adjustments). Included at `/predictions/`.
  - `predictions/services.py` — `process_match_result(match)` computes points (2 for correct winner, +2 for exact
    scoreline, +1 bonus if both are correct, max 5) and writes `PointTransaction` rows. Triggered from
    `MatchAdmin.save_model` whenever a match has both scores set; idempotent (re-running deletes and recreates that
    match's PREDICTION transactions).
  - `predictions/leaderboard.py` — `overall_leaderboard(group)` and `weekly_leaderboard(group, week_start_date)`
    rank a group's *approved* members by summed `PointTransaction.points`. Weeks are bucketed by
    `PointTransaction.week_date` (match kickoff date for prediction transactions, `created_at` for manual
    adjustments) via `week_start()` (Monday-anchored).

Cross-app dependency direction: `predictions` depends on `matches` (imports `Match`, `Outcome`) and `contests`
(imports `GroupMembership` for leaderboard membership/eligibility checks). `matches` does not depend on
`predictions` except in `matches/admin.py`, which calls `predictions.services.process_match_result`.

Templates live under the top-level `templates/` directory (`templates/<app>/...`), not inside each app, and all
extend `templates/base.html` (navbar + Bootstrap 5 via `django_bootstrap5` template tags).
