# Docker Development Guide — Madrona Portal (WCOA)

## Repository layout

This stack assumes the standard monorepo layout:

```
madrona-apps-claude/
├── madrona_portal/          ← main Django project (this repo)
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   └── entrypoint.sh
│   ├── Dockerfile
│   └── .env                 ← your local secrets (never committed)
└── madrona-apps/            ← sibling repo with all sub-app packages
    ├── wcoa/
    ├── mp-layers/
    └── ...
```

All commands below are run from the **`madrona_portal/`** directory unless noted.

---

## 1. Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine + Compose plugin (Linux)
- `madrona-apps/` checked out as a sibling of `madrona_portal/` (the Dockerfile copies from it at build time)

---

## 2. Configure environment

Copy the example and fill in real values:

```bash
cp .env.example .env   # if .env.example exists; otherwise edit .env directly
```

Minimum required values in `.env`:

```ini
SECRET_KEY=<random string>
DB_PASSWORD=<postgres password>
```

Other notable defaults (override in `.env` as needed):

| Variable | Default | Notes |
|---|---|---|
| `APP_PORT` | `8000` | Host port the Django app binds to |
| `DB_NAME` | `wcoa_docker_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PORT` | `5432` | Host port for PostgreSQL |
| `REDIS_PORT` | `6379` | Host port for Redis |
| `MP_PROJECT_CONFIG` | `config.wcoa.docker.ini` | Django config file (do not change for WCOA) |
| `DEBUG` | `False` | Set `True` to use Django dev server instead of gunicorn |
| `DJANGO_SUPERUSER_PASSWORD` | *(empty)* | If set, a superuser is created on first start |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Superuser username |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` | Superuser email |

---

## 3. Build the image

Use `docker buildx build` directly — `docker compose build` has a known caching issue where it silently reads committed (not filesystem) file versions when a `.git` directory exists in the build context.

From the **repo root** (`madrona-apps-claude/`):

```bash
docker buildx build \
    --builder desktop-linux \
    --load \
    -f madrona_portal/Dockerfile \
    -t madrona_portal-app:latest \
    .
```

Add `--no-cache` to force a full rebuild (e.g. after changing `requirements.txt`).

> **Important:** Always commit changes to `madrona_portal/` before rebuilding. BuildKit reads files from the git object store, not the filesystem, when a `.git` directory is present in the build context.

---

## 4. Start the full stack

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full up -d
```

The `--profile full` flag is required to start the `app` service. Without it, only `db` (PostGIS) and `tasks` (Redis) start — useful for running Django locally against Docker infrastructure.

Services:

| Service | Image | Host port |
|---|---|---|
| `app` | `madrona_portal-app:latest` | `${APP_PORT}` (default 8000) |
| `db` | `postgis/postgis:16-3.4` | `${DB_PORT}` (default 5432) |
| `tasks` | `redis:7-alpine` | `${REDIS_PORT}` (default 6379) |

---

## 5. What happens on first startup

The entrypoint (`docker/entrypoint.sh`) runs in order:

1. **Waits** for PostgreSQL to accept connections
2. **Migrates** (`manage.py migrate`)
3. **Collects static files** (`manage.py collectstatic`)
4. **Compresses assets** (`manage.py compress --force`)
5. **Seeds fixtures** — if fewer than 5 content pages exist (fresh DB), loads:
   - `apps/wcoa/wcoa/fixtures/initial_data_prod.json` (1,782 objects: pages, layers, themes, etc.)
   - `apps/madrona-scenarios/scenarios/fixtures/initial_data.json` (22 objects)
6. **Creates superuser** — only if `DJANGO_SUPERUSER_PASSWORD` is set and the username doesn't exist
7. **Starts the server** — gunicorn in production (`DEBUG=False`), Django dev server otherwise

Open: http://localhost:${APP_PORT}/

---

## 6. Dev infrastructure only (no app container)

To run Django locally with only the Docker DB and Redis:

```bash
docker compose -f docker/docker-compose.yml --env-file .env up -d
# db and tasks start; app does not (no --profile full)

cd marco
python manage.py runserver
```

---

## 7. Common one-off commands

```bash
# Django shell
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py shell

# Create superuser manually
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py createsuperuser

# Run migrations
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py migrate

# Load a fixture
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py loaddata /path/to/fixture.json

# Open a psql shell in the DB container
docker exec -it docker-db-1 psql -U postgres wcoa_docker_db
```

---

## 8. Rebuild after code changes

After changing Python source files, templates, or static assets in `madrona_portal/` or `madrona-apps/`:

1. Commit your changes (required for BuildKit to pick them up)
2. Rebuild from the repo root:
   ```bash
   docker buildx build --builder desktop-linux --load \
       -f madrona_portal/Dockerfile -t madrona_portal-app:latest .
   ```
3. Restart the app container:
   ```bash
   docker compose -f docker/docker-compose.yml --env-file .env --profile full \
       up -d --force-recreate app
   ```

---

## 9. Reset everything (fresh start)

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full down -v
```

`-v` removes the PostGIS and Redis volumes. Next `up` will re-run migrations and reload fixtures.

---

## 10. Disk space

Docker's build cache can grow large. Check usage and prune:

```bash
docker system df
docker system prune -f        # removes stopped containers, dangling images, unused networks, build cache
docker volume prune -f        # removes unused volumes (DESTRUCTIVE — removes DB data if containers are stopped)
```
