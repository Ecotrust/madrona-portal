# Docker Development Guide — Madrona Portal (WCOA)

## Quick start

These steps take a fresh machine from nothing to a running portal.

### Step 1 — Create the workspace directory

All repos live inside a single parent directory. The Dockerfile build
context is the parent, so the layout is not optional.

```bash
mkdir portals
cd portals
```

### Step 2 — Clone madrona-portal

```bash
git clone -b docker https://github.com/Ecotrust/madrona-portal.git madrona_portal
```

### Step 3 — Clone the sub-app packages

The Dockerfile copies all of these at build time. Clone them into a
`madrona-apps/` sibling directory:

```bash
mkdir madrona-apps && cd madrona-apps

git clone https://github.com/Ecotrust/django_url_shortener.git
git clone https://github.com/Ecotrust/madrona-analysistools.git
git clone https://github.com/Ecotrust/madrona-features.git
git clone https://github.com/Ecotrust/madrona-manipulators.git
git clone https://github.com/Ecotrust/madrona-scenarios.git
git clone https://github.com/Ecotrust/mp-accounts.git
git clone https://github.com/Ecotrust/mp-data-manager.git
git clone https://github.com/Ecotrust/mp-drawing.git
git clone https://github.com/Ecotrust/mp-explore.git
git clone https://github.com/Ecotrust/mp-layers.git
git clone https://github.com/Ecotrust/mp-map-groups.git
git clone https://github.com/Ecotrust/mp-proxy.git
git clone https://github.com/Ecotrust/mp-visualize.git
git clone https://github.com/Ecotrust/p97-nursery.git
git clone -b vagrant2docker https://github.com/Ecotrust/wcoa.git

cd ..
```

Your workspace should now look like:

```
portals/
├── madrona_portal/     ← cloned from Ecotrust/madrona-portal, branch: docker
└── madrona-apps/
    ├── wcoa/           ← branch: vagrant2docker
    ├── mp-layers/
    └── ...             ← all others on main
```

### Step 4 — Configure environment

From `madrona_portal/`:

```bash
cd madrona_portal
cp .env.example .env
```

Edit `.env` and set at minimum:

```ini
SECRET_KEY=<long random string>
DB_PASSWORD=<postgres password>
DJANGO_SUPERUSER_PASSWORD=<your dev admin password>
```

Everything else has working defaults for local development.

### Step 4.1 - Create ini file 

```bash
cd marco
cp config.docker.ini.template config.wcoa.docker.ini
```

Edit `config.wcoa.docker.ini` :

```ini
LOCATION = redis://tasks:6379/1
CELERY_RESULT_BACKEND = redis://tasks:6379/1
CELERY_BROKER_URL = redis://tasks:6379/0
```

### Step 5 — Build the image

Run this from the **workspace root** (`madrona_portal/`), not from
inside `madrona_portal/`. The build context must include both repos.

```bash
cd ../../   # back to portals/

docker buildx build \
    --builder desktop-linux \
    --load \
    -f madrona_portal/Dockerfile \
    -t madrona_portal-app:latest \
    .
```

This takes several minutes on a first build (compiling GDAL, installing
Python packages). Subsequent builds are fast thanks to layer caching.

> **Why `docker buildx build` and not `docker compose build`?**
> `docker compose build` has a caching bug: when a `.git` directory exists
> inside the build context, BuildKit reads files from the git object store
> (committed versions) rather than the filesystem. If you forget to commit
> a change, the old version is silently baked into the image. The same
> restriction applies — always commit changes to `madrona_portal/` or
> `madrona-apps/` before rebuilding.

### Step 6 — Start the full stack

From `madrona_portal/`:

```bash
cd madrona_portal

docker compose -f docker/docker-compose.yml --env-file .env --profile full up -d
```

The `--profile full` flag is required to start the `app` container.
Without it only `db` (PostGIS) and `tasks` (Redis) start.

On first boot the entrypoint automatically:

1. Waits for PostgreSQL to accept connections
2. Runs `migrate`
3. Runs `collectstatic` and `compress`
4. Detects a fresh database and loads initial fixtures (1,782 + 22 objects)
5. Creates the superuser defined in `.env` (if `DJANGO_SUPERUSER_PASSWORD` is set)
6. Starts the application server

Open: http://localhost:8000/ (or whatever `APP_PORT` is set to in `.env`)

### Step 7 - Importing a Production SQL Dump into the Dockerized Database

#### Prerequisites
- Docker Compose stack is running — `docker compose -f docker/docker-compose.yml --env-file .env --profile full up -d`
- `madrona_portal/.env` exists with `DB_NAME`, `DB_USER`, and `DB_PASSWORD` set


#### Step 7.1 — Ensure you have the db-restore script

`madrona_portal/scripts/db-restore.sh` has the following behaviour:
- Loads DB credentials from `.env`
- Verifies the `db` container is healthy before proceeding
- With `--drop`: terminates active connections, drops and recreates the database, and enables the PostGIS extension
- Streams the dump file directly into the container via `docker compose exec` (no temp files)
- Prints next-step instructions on completion

Made sure it is executable:
```bash
chmod +x madrona_portal/scripts/db-restore.sh
```


#### Step 7.2 — Run the restore

From `madrona_portal/`:
```bash
./scripts/db-restore.sh --drop <path_to_your_sql>
```
*example:*
```bash
./scripts/db-restore.sh --drop ../madrona-apps/wcoa/wcodp_prod_dump_20260320.sql
```

The `--drop` flag was used to ensure a clean import. The script:
1. Terminated all active connections to `wcoa_docker_db`
2. Dropped and recreated the database
3. Enabled the `postgis` extension
4. Streamed the sql dump into the container via `psql`

**Expected warnings (non-fatal):**
- `ERROR: relation "..." does not exist` — pg_dump tries to drop constraints before creating them; safe to ignore on a fresh DB
- `ERROR: role "wcoa_user" does not exist` — prod uses a dedicated app role; dev uses `postgres` which has full access


#### Step 7.3 — Apply migrations

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full exec app python marco/manage.py migrate
```

*Please note:* on 4/10/2026 a 130+ migrations were applied to bring the schema from the prod dump (PostgreSQL 12) up to date with the current codebase (PostgreSQL 16).


---  

# Untested instructions below this line — will update after testing

## Deploy to fully containerized live instance

1. Set up your `.env`
2. Build and run (from `portals/`):

```bash
docker buildx build \
    --builder desktop-linux \
    --load \
    -f madrona_portal/Dockerfile \
    -t madrona_portal-app:latest \
    .
```

### Redeploying after code changes

Then from `madrona_portal/`:

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    up -d --force-recreate app
```

Add `--no-cache` to the buildx command to force a full dependency reinstall
(needed when `docker-requirements.txt` changes).

---

## Everyday usage

All `docker compose` commands below are run from **`madrona_portal/`**.

### View logs

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full logs -f app
```

### Run a management command

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py <command>
```

Examples:

```bash
# Django shell
... run --rm app python marco/manage.py shell

# Create superuser manually
... run --rm app python marco/manage.py createsuperuser

# Load a fixture
... run --rm app python marco/manage.py loaddata /path/to/fixture.json
```

### Open a database shell

```bash
docker exec -it docker-db-1 psql -U postgres wcoa_docker_db
```

---

## Dev infrastructure only (local Django server)

To run Django locally against Docker-managed PostGIS and Redis (no app container):

```bash
# Start only db and tasks (omit --profile full)
docker compose -f docker/docker-compose.yml --env-file .env up -d

# Then in a separate terminal, from madrona_portal/:
cd marco
python manage.py runserver
```

---

## Rebuilding after code changes

> **Commit first.** BuildKit reads from the git object store — uncommitted
> changes are invisible to the build.

From the **workspace root** (`portals/`):

```bash
docker buildx build \
    --builder desktop-linux \
    --load \
    -f madrona_portal/Dockerfile \
    -t madrona_portal-app:latest \
    .
```

Then from `madrona_portal/`:

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    up -d --force-recreate app
```

Add `--no-cache` to the buildx command to force a full dependency reinstall
(needed when `docker-requirements.txt` changes).

---

## Reset to a clean state

```bash
# From madrona_portal/
docker compose -f docker/docker-compose.yml --env-file .env --profile full down -v
```

`-v` removes the PostGIS and Redis volumes. The next `up` will re-run
migrations and reload fixtures from scratch.

---

## Services and ports

| Service | Image | Default host port | Override via |
|---|---|---|---|
| `app` | `madrona_portal-app:latest` | `8000` | `APP_PORT` in `.env` |
| `db` | `postgis/postgis:16-3.4` | `5432` | `DB_PORT` in `.env` |
| `tasks` | `redis:7-alpine` | `6379` | `REDIS_PORT` in `.env` |

---

## Disk space

Docker's build cache can grow large over time:

```bash
docker system df                  # show usage breakdown
docker system prune -f            # remove stopped containers, dangling images, unused networks, build cache
docker volume prune -f            # remove unused volumes — only run when all containers are stopped
```
