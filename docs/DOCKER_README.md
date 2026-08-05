# Docker Development Guide - Madrona Portal Platform

This guide describes the decoupled Docker model for Madrona.

Use this file for platform-level Docker concepts and core-image development.
For portal-specific workflows, use each portal repository documentation.

## 1. Architecture summary

Madrona uses a two-layer image architecture:

- Core base image: `ghcr.io/ecotrust/madrona-portal:{sha,latest}`
- Portal overlays: each portal builds from the base and publishes its own image.

The core repo should remain portal-agnostic:

- No portal app code copied into core Docker image.
- No portal-only services in core compose definitions.
- No portal-specific config file paths in core defaults.

## 2. Workspace layout

A sibling workspace is still expected for local development:

```text
madrona/
├── madrona-portal/
└── madrona-apps/
    ├── wcoa/
    ├── mida-portal/
    └── ...shared apps...
```

## 3. Core image purpose

The core image contains:

- Ubuntu runtime and system packages.
- Python environment and shared dependencies.
- Core Django project (`marco`) and entrypoint.
- Shared Madrona/MP app packages.

The core image does not include a deployable portal by itself.

## 4. Compose layering model

Use a base + overlay compose pattern:

- Core base compose: `madrona-portal/docker/compose.base.yml`
- Portal overlay compose: `<portal>/docker/compose.yml`
- Production image compose: `<portal>/docker/compose.prod.yml`

Rules:

- Keep path-sensitive bind mounts declared in the portal compose file.
- Use unique `COMPOSE_PROJECT_NAME` per portal.
- Keep portal-only services in portal compose files.

## 5. Typical local flow

From a portal repository (example: WCOA):

```bash
cp docker/.env.example docker/.env
```

Build base image if shared dependencies changed:

```bash
task base
```

Build and run portal overlay stack:

```bash
task build
task up
```

Initialize schema/fixtures on first boot only:

```bash
task init
```

## 6. Production-oriented flow

Production hosts pull portal overlay images from GHCR.

Typical commands from portal repo:

```bash
docker compose -f docker/compose.prod.yml --env-file docker/.env pull
docker compose -f docker/compose.prod.yml --env-file docker/.env up -d
```

Rollback is performed by setting a previous image tag in `docker/.env` and rerunning the same commands.

## 7. Portal documentation pointers

- Core host guide: `madrona-portal/docs/AWS_DEPLOY.md`
- New portal checklist: `madrona-portal/docs/NEW_PORTAL_CHECKLIST.md`
- WCOA deploy runbook: `madrona-apps/wcoa/docs/AWS_DEPLOY_WCOA.md`
- WCOA cutover runbook: `madrona-apps/wcoa/docs/PRODUCTION_CUTOVER.md`

## 8. Cleanup commands

Check Docker usage:

```bash
docker system df
```

Clean unused resources:

```bash
docker system prune -f
docker volume prune -f
```

Use volume cleanup with care; stop running stacks first.
