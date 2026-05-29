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
git clone -b docker https://github.com/Ecotrust/madrona-portal.git madrona-portal
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
git clone https://github.com/Ecotrust/mp-survey.git
git clone https://github.com/Ecotrust/mp-visualize.git
git clone https://github.com/Ecotrust/p97-nursery.git
git clone https://github.com/Ecotrust/wcoa.git

cd ..
```

Your workspace should now look like:

```
portals/
├── madrona-portal/     ← cloned from Ecotrust/madrona-portal, branch: docker
└── madrona-apps/
    ├── wcoa/           ← branch: vagrant2docker
    ├── mp-layers/
    └── ...             ← all others on main
```

### Step 4 — Configure environment

From `madrona-portal/`:

```bash
cd madrona-portal/docker
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
cd ../marco
cp config.docker.ini.template config.wcoa.docker.ini
```

Edit `config.wcoa.docker.ini` :

```ini
LOCATION = redis://tasks:6379/1
CELERY_RESULT_BACKEND = redis://tasks:6379/1
CELERY_BROKER_URL = redis://tasks:6379/0
```

### Step 5 — Build the image

Run this command from `madrona-portal/docker` (the previous step leaves
you in `madrona-portal/marco`, so `cd ../docker` gets you there). The
Docker build context for this command is `../../`, which resolves to the parent workspace directory `portals/` that contains both
`madrona-portal/` and `madrona-apps/`.

If running this build from a MAC, add `--builder desktop-linux` to the `buildx build` command. 

```bash
cd ../docker
# MAC OS
docker compose build --no-cache app
# LINUX
docker compose build --no-cache app
```

Previously we recommended `docker buildx build --builder desktop-linux --no-cache --load -f ./Dockerfile ../../` for all platforms, but BuildKit caching on Linux does not appear to have the same git object store issue as on Mac, so the simpler `docker compose build --no-cache app` is sufficient on Linux.

> **Why `docker buildx build` and not `docker compose build`?**
> `docker compose build` has a caching bug: when a `.git` directory exists
> inside the build context, BuildKit reads files from the git object store
> (committed versions) rather than the filesystem. If you forget to commit
> a change, the old version is silently baked into the image. The same
> restriction applies — always commit changes to `madrona-portal/` or
> `madrona-apps/` before rebuilding.

### Step 6 — Start the full stack; Populate testing DB

From `madrona-portal/docker`:

```bash
DB_INIT=1 docker compose up
```

On first boot the entrypoint automatically:

1. Waits for PostgreSQL to accept connections
2. Runs `migrate`
3. Runs `collectstatic` and `compress`
4. Detects a fresh database and loads initial fixtures (1,782 + 22 objects)
5. Creates the superuser defined in `.env` (if `DJANGO_SUPERUSER_PASSWORD` is set)
6. Starts the application server

Open: http://localhost:8000/ (or whatever `APP_PORT` is set to in `.env`)

Once you have a populated DB (either dummy or with migrated data) omit the `DB_INIT=1`:
```bash
docker compose up
```


### Step 7 - Importing a Production SQL Dump into the Dockerized Database

#### Prerequisites
- Docker Compose stack is running — `docker compose up`
- `madrona-portal/docker/.env` exists with `DB_NAME`, `DB_USER`, and `DB_PASSWORD` set


#### Step 7.1 — Ensure you have the db-restore script

`madrona-portal/scripts/db-restore.sh` has the following behaviour:
- Loads DB credentials from `.env`
- Verifies the `db` container is healthy before proceeding
- With `--drop`: terminates active connections, drops and recreates the database, and enables the PostGIS extension
- Streams the dump file directly into the container via `docker compose exec` (no temp files)
- Prints next-step instructions on completion

Made sure it is executable:

From `madrona-portal/docker`:
```bash
chmod +x ../scripts/db-restore.sh
```

#### Step 7.2 — Run the restore

From `madrona-portal/docker`:
```bash
../scripts/db-restore.sh --drop <path_to_your_sql>
```

*example:*
```bash
../scripts/db-restore.sh --drop ../../madrona-apps/wcoa/wcodp_prod_dump_20260320.sql
```

The `--drop` flag was used to ensure a clean import. The script:
1. Terminated all active connections to `wcoa_docker_db`
2. Dropped and recreated the database
3. Enabled the `postgis` extension
4. Streamed the sql dump into the container via `psql`

There is an optional `--env-file <path_to_your_env_file>` if you place your `.env` file in a non-standard location.

**Expected warnings (non-fatal):**
- `ERROR: relation "..." does not exist` — pg_dump tries to drop constraints before creating them; safe to ignore on a fresh DB
- `ERROR: role "wcoa_user" does not exist` — prod uses a dedicated app role; dev uses `postgres` which has full access


#### Step 7.3 — Apply migrations

```bash
docker compose exec app python marco/manage.py migrate
```

#### Step 7.4 - Migration to mp-layers

*If migrating from a server that has not migrated to mp-layers from mp-data-manager*:

```bash
docker compose exec app python marco/manage.py migration_to_layers
```

---  

### Step 8 — Importing production media files into the Dockerized Application

#### Prerequisites
- `madrona-portal/marco/marco/config.wcoa.docker.ini` exists with `MEDIA_ROOT` set to a valid directory
- That valid directory should match the volume location is docker-compose.yml
   - `portals/madrona-portal/media`
- Production media files are available 

#### Step 8.1 - Copy the media files into Docker

If media files need to be copied to the server, you can use `scp`:

```bash
scp -r /path/to/your_media_dir ubuntu@<ELASTIC_IP>:/home/ubuntu/portals/madrona-portal/docker/media
```

If media files are somewhere on EC2:

```bash
cd ~/portals/madrona-portal/docker
cp -r {your_media_dir}/* ./media/
```

#### Create a directory for data_manager
```bash
mkdir ~/portals/madrona-portal/docker/data_manager
```

---  

## Migrate existing GeoPortal records

1. Update .env with the reindex remote whitelist and port. You can find this info by looking at the old server's configuration or by asking the previous admin.

2. Edit the hosts file to allow the server to resolve the old Elastic IP of the GeoPortal instance to the new internal Docker network:

```bash
sudo vim /etc/hosts
# Add the following line, replacing <OLD_ELASTIC_IP> and <ES_REINDEX_REMOTE_WHITELIST from .env>:
<OLD_IP> <ES_REINDEX_REMOTE_WHITELIST from .env>
```

3. Restart the elastic container to apply the .env and hosts file change:

```bash
docker compose down -v elastic
docker compose up -d elastic
```

4. Ensure the app is running, you can migrate existing GeoPortal records with the following command (replace the username and password):

```bash
time curl -X POST "http://localhost:9200/_reindex"  -H 'Content-Type: application/json' -d'{"conflicts": "proceed", "max_docs": 51000, "source": {"remote": { "host":"http://elastic.prod.wcoa.ecotrust.org:80/geoportal/elastic/", "username": "[[USERNAME]]", "password": "[[PASSWORD]]"  }, "index": "metadata", "size": 100 }, "dest": { "index": "metadata" } }'
```

1. Do a down, including volumes, and up for the geoportal container to pick up the new records:

```bash
docker compose down -v geoportal
docker compose up -d geoportal
```

---

# Deploy to fully containerized production environment

## AWS EC2

See [AWS_DEPLOY.md](../docs/AWS_DEPLOY.md)

---  

## Dev infrastructure only (local Django server)

To run Django locally against Docker-managed PostGIS and Redis (no app container):

```bash
# Start only db and tasks
docker compose up -d db tasks

# Then in a separate terminal, from madrona-portal/:
cd marco
python manage.py runserver
```

---

## Rebuilding after code changes

From the docker directory (`madrona-portal/docker`):

```bash
docker compose build --no-cache app
```

| Note on `--no-cache`: Use it when dependencies have changed; without it, Docker reuses the cached pip install layer (needed when `docker-requirements.txt` changes).

Then bring the stack up:

```bash
docker compose up --force-recreate
```

---

## Reset to a clean state

```bash
# From madrona-portal/
docker compose -f docker/docker-compose.yml --env-file .env --profile full down -v
```

`-v` removes the PostGIS and Redis volumes. The next `up` will re-run
migrations and reload fixtures from scratch.

---

## Disk space

Docker's build cache can grow large over time:

```bash
docker system df                  # show usage breakdown
docker system prune -f            # remove stopped containers, dangling images, unused networks, build cache
docker volume prune -f            # remove unused volumes — only run when all containers are stopped
```
