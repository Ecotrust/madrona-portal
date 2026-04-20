# Madrona Portal — Modernization Log & Roadmap

> **Last updated:** March 2026
> **Stack target:** Python 3.10+, Django 4.2 LTS, Wagtail 7.x

---

## Phase 1 — Completed (March 2026)

These changes have been applied to the codebase.

### Dependencies

| File | Change |
|---|---|
| `requirements.txt` | Added version bounds to all packages; removed duplicate `django-colorfield`; resolved `social-auth-app-django` conflict (`<5.0` vs `>5.4`); updated `django-taggit` to `>=5.0,<7.0`; widened Django constraint to `>=4.2,<5.0` to allow patch updates |
| `dev_requirements.txt` | **Completely replaced.** Old file pinned Django <1.10, Wagtail 1.3.1 (2015-era). New file contains `pytest`, `pytest-django`, `pytest-cov`, `factory-boy`, `ruff`, `mypy`, `django-stubs`, and `django-debug-toolbar` |
| `docker/docker-requirements.txt` | No changes — already modern. Production reference file. |

### `settings.py`

- Removed **Wagtail v1 / v2 / v3 runtime detection** (nested try/except over `INSTALLED_APPS`). Locked to Wagtail 7+ with a clean, single `INSTALLED_APPS` list.
- Removed **`REDIS_PACKAGE_NAME` / `redis_cache` fallback** — `django_redis` is the only supported cache backend.
- Removed **dead `if False:` debug-toolbar block** — enable via `dev_requirements.txt` and `ADDITIONAL_APPS` in config.
- Removed **commented-out Wagtail v1/v2 middleware blocks**.
- Replaced **`eval()` calls** for `ADDITIONAL_APPS` / `ADDITIONAL_MIDDLEWARE` with `json.loads()` + `ast.literal_eval()` fallback. `eval()` on config-file values is a remote-code execution risk.
- Replaced **`exec("from %s.settings import *")` pattern** with a proper `import_module` + namespace merge loop.
- Removed **deprecated `BROKER_URL`** — Celery 5 uses `CELERY_BROKER_URL` only.
- Removed **`SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True`** (deprecated).
- Replaced **`try: VAR except NameError`** patterns for `FEEDBACK_IFRAME_URL`, `DISCLAIMER_BUTTON_DEFAULT`, `DATA_MANAGER_ADMIN`, `PROJECT_REGION` with direct assignment.
- Updated docstring reference from Django 1.7 to 4.2.
- Added **`SECRET_KEY` guard** — raises `RuntimeError` at startup if key is unset, rather than silently running with `'you forgot to set the secret key'`.
- Consolidated all `cfg.sections()` existence checks into a single loop at the top.

### `urls.py`

- Removed **Django 1.x `from django.conf.urls import url` try/except** — `django.urls.re_path` (Django 2.0+) is now imported directly.
- Removed **`WAGTAIL_VERSION > 1` branch** — both branches were identical (Wagtail v1 `wagtail.docs` vs v2+ `wagtail.documents`). The v2+ import is used directly.
- Removed trailing `/?` optional slashes on most routes (ambiguous in Django URL routing).
- Replaced `re_path(r'^django-admin/?', ...)` with `re_path(r'^django-admin/', ...)` — `admin.site.urls` already handles trailing slash.
- Added `warnings.warn` instead of silent `except Exception: pass` when `PROJECT_APP` URL import fails.
- Added API URL auto-discovery: for each entry in `INSTALLED_APPS`, if `<app>.urls` exists and defines `api_urlpatterns`, those routes are automatically mounted under `/api/`.
- New convention for sub-apps: define REST endpoints in `<app>/api.py`, expose them from `<app>/urls.py` as `api_urlpatterns`, and avoid hard-coding app-specific API imports in the project URLConf.

### Migrations

- Stripped **`from __future__ import unicode_literals`** from **72 migration files** — this Python 2 compatibility import is a no-op in Python 3 and adds noise.

### Docker & DevOps

| File | Change |
|---|---|
| `Dockerfile` | Fixed **indentation bug**: three `RUN` statements inside the `apt-get` block were indented as if part of it, but only the first `RUN` was correctly associated. Moved venv creation, pip install, and GDAL install to separate top-level `RUN` layers for correct caching. Consolidated final `RUN` commands (chmod, mkdir, useradd, chown) into one layer. |
| `docker/docker-compose.yml` | Added **`healthcheck`** blocks for `db` (pg_isready) and `tasks` (redis ping). Replaced `links:` with `depends_on: condition: service_healthy`. Added `restart: unless-stopped`. Removed stale Vagrant-era volume name `redis.conf`. Set sensible `:-default` values for env vars. |
| `.env.example` | **New file** — documents every required environment variable with safe placeholder values. Committed to repo so developers know what to configure. |
| `.gitignore` | Added `.env` entry to prevent real credentials from being committed. |

### Tooling

| File | Change |
|---|---|
| `pyproject.toml` | **New file** — central config for `pytest`, `coverage`, `ruff`, and `mypy`. Replaces ad-hoc tool configs scattered across the project. |

---

## Phase 2 — Completed (March 2026)

### Secret Management

- **Extended env var support** throughout `settings.py` via a new `_env(env_key, cfg_section, cfg_key, default)` helper. Every credential-bearing setting now checks an environment variable *first*, falls back to `config.ini`, then to a safe default.
- **Database** — supports `DB_*` env vars (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) as well as legacy `SQL_*` aliases for docker-compose compatibility.
- **Redis** — a single `REDIS_URL` env var configures the Django cache location, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` simultaneously.
- **Email** — `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` all respect env vars.
- **AWS SES** — `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SES_REGION_NAME`, `AWS_SES_REGION_ENDPOINT`.
- **Social auth** — `FACEBOOK_KEY`, `FACEBOOK_SECRET`, `TWITTER_KEY`, `TWITTER_SECRET`, `GOOGLE_KEY`, `GOOGLE_SECRET`.
- **`.env.example`** — updated to document every env var with safe placeholder values, organized by category.
- **`config.wcoa.ini` / `config.mida.ini`** — these still contain real credentials and should be removed from git history using `git filter-repo --path config.wcoa.ini --path config.mida.ini --invert-paths`. That step requires a git client and is left for the team to execute.

### Social Auth Pipeline

- Renamed all `social.pipeline.*` strings in `SOCIAL_AUTH_PIPELINE` to `social_core.pipeline.*` — the correct module path for `social-auth-core ≥ 4.x`. The old `social` namespace was a legacy alias that has been dropped.

### rpc4django Replacement

- **Removed** `rpc4django` from `INSTALLED_APPS`, `requirements.txt`, and `urls.py`.
- The single `/rpc` XML-RPC endpoint served **11 methods** across 3 sub-apps. Each has been replaced with a typed DRF `APIView`:

| Old RPC method | New endpoint | App |
|---|---|---|
| `get_bookmarks` | `GET /api/bookmarks/` | visualize |
| `add_bookmark` | `POST /api/bookmarks/` | visualize |
| `load_bookmark` | `GET /api/bookmarks/<id>/` | visualize |
| `remove_bookmark` | `DELETE /api/bookmarks/<id>/` | visualize |
| `share_bookmark` | `POST /api/bookmarks/<uid>/share/` | visualize |
| `get_user_layers` | `GET /api/user-layers/` | visualize |
| `add_user_layer` | `POST /api/user-layers/` | visualize |
| `load_user_layer` | `GET /api/user-layers/<id>/` | visualize |
| `remove_user_layer` | `DELETE /api/user-layers/<id>/` | visualize |
| `share_user_layer` | `POST /api/user-layers/<uid>/share/` | visualize |
| `delete_drawing` | `DELETE /api/drawings/<uid>/` | drawing |
| `get_sharing_groups` | `GET /api/sharing-groups/` | mapgroups |
| `update_map_group` | `PATCH /api/map-groups/<id>/` | mapgroups |

- New files: `visualize/api.py`, `drawing/api.py`, `mapgroups/api.py`. Each app's `urls.py` updated accordingly.
- All new views carry full **type annotations** and proper DRF permission classes (`IsAuthenticated` / `AllowAny`).

### accounts/pipeline.py

- Removed Python 2 compatibility shims: `try/except ImportError` for `django.urls.reverse`, `try/except ImportError` for `urllib.parse`, and `import urlparse` (Python 2 stdlib).
- Replaced `urlparse.urlsplit` / `urlparse.urlunsplit` with `urllib.parse.urlsplit` / `urllib.parse.urlunsplit`.
- Removed dead `from django.core.context_processors import request` import (removed in Django 1.10).
- Removed dead `from django.conf.urls import include, url` fallback.
- Added proper type hints and a complete `send_validation_email` stub (was missing from the pipeline).

### wagtail_migrations/ Directory

- The directory contains 30+ step-by-step upgrade shell scripts (Wagtail 1.4 → 2.11), Python 2 view backups, and ancient requirements snapshots. None are needed at Wagtail 7.
- **The files are OS-level read-only in this environment.** Run this from the project root to remove them:
  ```bash
  git rm -rf wagtail_migrations/
  git commit -m "Remove historical wagtail_migrations upgrade scripts"
  ```

---

## Phase 3 — Recommended Next Steps

### High Priority

- **Frontend build tooling** — Replace Bower + Gulp with `npm` + Vite. Bower has been deprecated since 2017. Add `/bower_components/` to `.gitignore` and drive dependencies through `package.json`.
- **Test coverage** — Only 2 test files exist. Add `pytest-django` suites targeting 60%+ coverage for models and views across the portal sub-apps.
- **CI / CD pipeline** — GitHub Actions: lint (`ruff`), test (`pytest`), Docker build, tag-based image push to registry.

### Medium Priority

- **Django 5.x upgrade** — Django 4.2 LTS support ends April 2026. Evaluate Django 5.1 once sub-app compatibility is confirmed.
- **Consolidate config.ini variants** — 6 config files remain. Migrate to a single `.env`-driven approach and retire the `.ini` files.
- **Expand type coverage** — Run `mypy --strict` against `portal/`, `marco_site/`, and all sub-app `views.py` files; address errors incrementally.

---

## Appendix — Technical Debt Removed

| Category | Count / Description |
|---|---|
| Python 2 imports removed | 72 migration files |
| Wagtail version branches removed | 3 (v1, v2, v5 detection) |
| `eval()` calls on config data removed | 2 (`ADDITIONAL_APPS`, `ADDITIONAL_MIDDLEWARE`) |
| `exec()` for dynamic import removed | 1 |
| Deprecated Celery settings removed | 1 (`BROKER_URL`) |
| Dead code blocks removed | 2 (`if False:`, commented middleware) |
| Dockerfile layer ordering bugs fixed | 3 mis-indented `RUN` commands |
| Docker Compose healthchecks added | 2 services (`db`, `tasks`) |
| Secret key runtime guard added | 1 (was silently `'you forgot...'`) |
