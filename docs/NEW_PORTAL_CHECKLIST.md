# New Portal Deployment Checklist

Use this checklist when bringing a new portal onto the Madrona Docker platform.

Goal:

- Deploy a new portal using only portal-repo changes plus host/runtime configuration.
- Avoid editing core deployment logic for portal-specific behavior.

Prerequisites:

- Core host setup completed via `docs/AWS_DEPLOY.md`.
- Core base image is published and available in GHCR.
- New portal repository exists and is accessible from deployment host and CI.

## 1. Create portal Docker layout

In the portal repository, create:

```text
docker/
  Dockerfile
  compose.yml
  compose.prod.yml
  .env.example
  config.<portal>.docker.ini
  config.<portal>.prod.ini
  static/
  media/
  backups/
```

Rules:

- Keep portal-specific runtime config in portal repo.
- Keep secrets out of ini files and out of git.
- Put secrets in `docker/.env` on each host.

## 2. Build overlay image from base image

Create a portal overlay Dockerfile pattern:

```dockerfile
ARG BASE_IMAGE=ghcr.io/ecotrust/madrona-portal
ARG BASE_TAG=latest
FROM ${BASE_IMAGE}:${BASE_TAG}

COPY --chown=madrona_user:madrona_user . ./apps/<portal>

RUN pip install --no-deps -e ./apps/<portal> && \
    if [ -s ./apps/<portal>/docker/requirements.txt ]; then \
      pip install -r ./apps/<portal>/docker/requirements.txt; \
    fi

ENV MP_PROJECT_CONFIG=/usr/local/apps/madrona-portal/apps/<portal>/docker/config.<portal>.docker.ini
```

## 3. Add portal image CI workflow

Create `.github/workflows/build-and-publish-image.yml` in the portal repo.

Minimum requirements:

- Trigger on `main` and deployment branch as needed.
- Build with `docker/build-push-action`.
- Push `ghcr.io/<org>/<portal-image>:<short-sha>` and `:latest`.
- Define multi-arch platforms:

```yaml
env:
  IMAGE_PLATFORMS: linux/amd64,linux/arm64
```

Validation:

- Confirm package exists in GHCR.
- Confirm pull works from a clean host.

## 4. Define compose project identity and port plan

Set in `docker/.env.example`:

- `COMPOSE_PROJECT_NAME=<portal>`
- `APP_PORT=<host-app-port>`
- `DB_PORT=<host-db-port>` (if local host access is needed)

Rules:

- `COMPOSE_PROJECT_NAME` must be unique per portal on shared hosts.
- Host ports must not overlap with other portal stacks.
- Keep internal container ports unchanged unless intentionally redesigned.

## 5. Configure portal ini files

Create two non-secret ini files:

- `docker/config.<portal>.docker.ini` for local development defaults.
- `docker/config.<portal>.prod.ini` for production-oriented non-secret defaults.

Required checks:

- `PROJECT_APP=<portal-app-name>` is correct.
- `PROJECT_SETTINGS_FILE=True` if portal settings module is used.
- Production ini sets `DEBUG=False`.
- Production catalog/search endpoints point to in-stack services where applicable.
- Email identity values are portal-correct (no copied values from other portals).

## 6. Author `docker/.env.example`

Include all required runtime variables with empty or safe defaults.

Required fields typically include:

- `BASE_TAG`
- `IMAGE_TAG`
- `SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `REDIS_PASSWORD`
- `DB_INIT`
- `DJANGO_ENV`
- Any portal-specific integration keys

Rules:

- Never commit populated production `.env`.
- Document required secrets source for operators.

## 7. Compose production wiring

In `docker/compose.prod.yml`:

- Set app image to the portal GHCR image.
- Mount and reference `config.<portal>.prod.ini`.
- Set `MP_PROJECT_CONFIG` to the mounted in-container path.
- Ensure host-to-container app mapping is explicit.

Example mapping pattern:

```yaml
ports:
  - "${APP_PORT:-8000}:8008"
```

## 8. Nginx integration

Create portal server block from core template:

- Proxy `/` to `127.0.0.1:${APP_PORT}`.
- Serve static/media from portal paths.
- Add portal-only upstream routes as needed.

Rules:

- Use loopback targets (`127.0.0.1`) for local services.
- Do not proxy to public instance IP from same host.

## 9. systemd unit

Create one unit per portal (for example `<portal>.service`).

Required values:

- `WorkingDirectory=/home/ubuntu/portals/<portal>/docker`
- `ExecStart=docker compose -f compose.prod.yml --env-file .env up -d`
- `ExecStop=docker compose -f compose.prod.yml --env-file .env down`

Enable and test restart behavior before go-live.

## 10. Backup and cron ownership

Place backup/snapshot scripts in the portal repo under `scripts/`.

Install portal cron entries for:

- PostgreSQL dump and retention.
- Search/index snapshots (if portal uses search service).
- Portal-specific data refresh jobs.

Rules:

- Cron should call portal paths only.
- Backup output paths should be under portal `docker/backups/`.

## 11. Portal runbook docs

Create a portal deployment runbook based on WCOA templates:

- `docs/AWS_DEPLOY_<PORTAL>.md`
- Optional: `docs/PRODUCTION_CUTOVER.md`

Runbook must include:

- Artifact placement.
- Host `.env` requirements.
- First boot/init sequence.
- Data restore sequence.
- Verify checklist.
- Rollback commands.

## 12. Validation gate before production

Minimum validation:

- CI build succeeded and image pull verified.
- `docker compose config` renders cleanly for prod file.
- App boots with `DB_INIT=0` and healthy dependencies.
- Login and representative user flows pass.
- Backup and snapshot jobs run successfully in dry-run.
- Rollback command tested in staging.

## 13. Done criteria

A portal onboarding is complete when:

- Production deployment requires no edits to `madrona-portal/docs/AWS_DEPLOY.md`.
- All portal-specific deployment behavior lives in portal repo docs/config/scripts.
- Operators can deploy and rollback from portal docs alone.
