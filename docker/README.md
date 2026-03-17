# WCOA Docker Development Guide

This guide switches local development from the Vagrant workflow to Docker
Compose for `madrona_portal` + `wcoa`.

It is aligned with the install process documented in the project wiki:
https://github.com/Ecotrust/madrona-portal/wiki/Installation

## 1) Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Local checkout layout where this repository has sibling module directories in
  `../madrona-apps` (already true in this workspace)

## 2) Keep companion apps checked out

The Docker image installs local editable dependencies from
`/usr/local/apps/madrona-portal/apps/...`, so keep companion repos present in
`../madrona-apps` as referenced by `docker/docker-requirements.txt`.

## 3) Set Docker environment values

Edit `docker/.env` and set at minimum:

- `SECRET_KEY`
- `SQL_DATABASE`
- `SQL_USER`
- `SQL_PASSWORD`
- `ALLOWED_HOSTS`

Default local ports in this repo:

- Django app: `8000`
- PostGIS on host: `65432`
- Redis on host: `8379`

## 4) Use the Docker-specific WCOA Django config

Compose is configured to run with:

- `MP_PROJECT_CONFIG=config.wcoa.docker.ini`

That file lives at `marco/config.wcoa.docker.ini` and points Django to:

- PostGIS host `db`
- Redis host `tasks`
- Container-friendly static/media paths under `/vol/web`

## 5) Build and start

From `madrona_portal/`:

```bash
cd docker
docker compose --env-file .env up --build
```

The entrypoint waits for PostGIS, then runs:

- `collectstatic`
- `migrate`
- `runserver 0:8000`

Open: http://localhost:8000/

## 6) Common one-off commands

From `madrona_portal/docker`:

```bash
docker compose --env-file .env run --rm app python marco/manage.py createsuperuser
docker compose --env-file .env run --rm app python marco/manage.py shell
docker compose --env-file .env run --rm app python marco/manage.py loaddata /path/to/fixture.json
```

## 7) Data migration from old Vagrant DB

If you are moving existing data, dump from Vagrant PostgreSQL and import into the
Docker `db` service:

```bash
# Example import into running Docker DB
cat ./path/to/old_dump.sql | docker compose --env-file .env exec -T db psql -U "$SQL_USER" -d "$SQL_DATABASE"
```

## 8) Stop and clean up

```bash
docker compose --env-file .env down
docker compose --env-file .env down -v  # also removes PostGIS/Redis volumes
```

## Notes

- The legacy Vagrant flow in the top-level README remains valid, but Docker is
  faster for repeatable local startup.
- If you need to run with a different portal app (for example `mida` or
  `offshore`), create another config file modeled on
  `marco/config.wcoa.docker.ini` and set `MP_PROJECT_CONFIG` accordingly.
