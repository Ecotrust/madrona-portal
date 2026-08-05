# AWS Host Setup - Madrona Portal Platform

This guide covers platform-level deployment setup on AWS for Dockerized Madrona portals.
It is intentionally portal-agnostic and stops at a host that is ready to run any portal-specific runbook.

## 1. Deployment model

Madrona deployment uses a two-image model:

- Base image: shared platform/runtime image published from core.
- Overlay image: portal image that layers portal code/config over the base.

Runtime behavior:

- Production hosts run overlay images only.
- Base image rebuilds alone do not change production behavior.
- Shared-code changes require rebuilding base, then rebuilding each portal overlay against the new base tag.

Tagging guidance:

- Prefer pinned SHA tags in production for both base and overlay references.
- Use `latest` only for development/testing.

## 2. Prerequisites

- AWS account with EC2 permissions.
- GitHub access to required container packages.
- Domain and DNS control for TLS setup.
- SSH client and private key management process.

## 3. GHCR setup (one-time)

### 3.1 CI push permissions

Ensure CI workflows that publish images can write packages in GHCR.
Use short-lived or rotated credentials and least privilege where possible.

### 3.2 Host pull permissions

Create a read-only token for deployment hosts to pull container images.
Store it in host secret storage and run login on-host:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

### 3.3 Verify image availability

Before host rollout, confirm the target image tags exist:

```bash
docker manifest inspect ghcr.io/<org>/<portal-image>:<image-tag> >/dev/null
```

## 4. AWS infrastructure baseline

### 4.1 EC2

- Recommended baseline for app + db + redis only: `t3.medium`.
- Increase instance class when portal overlays include extra services (search engines, catalog systems, app servers).
- Start with at least 40-60 GB gp3 root volume for logs, images, and backups.

### 4.2 Security group

Allow inbound only as needed:

- `22/tcp` from restricted admin CIDRs.
- `80/tcp` and `443/tcp` from internet.

Do not expose internal service ports publicly (`5432`, `6379`, `9200`, `9300`, app container ports).

### 4.3 Elastic IP

Associate an Elastic IP for stable DNS mapping and easier cutovers.

## 5. Server setup

All commands assume Ubuntu.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker "$USER"
```

Re-login after adding your user to the docker group.

Optional host hardening:

- Enable unattended upgrades.
- Add swap for memory pressure protection.
- Install baseline monitoring (for example Munin or CloudWatch agent).

## 6. Host layout for portal repos

Use one directory per portal checkout:

```text
/home/ubuntu/portals/
  portal-a/
  portal-b/
```

Each portal directory should contain:

- Portal compose files.
- Portal `.env` file (not committed).
- Portal production config ini file(s).
- Portal static/media/backups directories as needed.

For web-serving through Nginx, ensure traversal permissions allow the web user to read required paths.

## 7. Nginx and TLS pattern

### 7.1 Install and obtain certificates

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Create a basic server block for the portal domain, then run:

```bash
sudo certbot --nginx -d <portal-domain> -d <optional-www-domain>
```

### 7.2 Reverse proxy skeleton

```nginx
server {
    listen 80;
    server_name <portal-domain> <optional-www-domain>;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name <portal-domain> <optional-www-domain>;

    ssl_certificate /etc/letsencrypt/live/<portal-domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<portal-domain>/privkey.pem;

    client_max_body_size 100M;

    location /static/ {
        alias /home/ubuntu/portals/<portal>/docker/static/;
    }

    location /media/ {
        alias /home/ubuntu/portals/<portal>/docker/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:<app-host-port>;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
}
```

Portal-specific upstream routes for extra services belong in that portal runbook.

## 8. systemd service pattern

Use one unit per portal stack to keep services isolated.

Example unit:

```ini
[Unit]
Description=Portal Docker Stack (<portal>)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/portals/<portal>/docker
ExecStart=/usr/bin/docker compose -f compose.prod.yml --env-file .env up -d
ExecStop=/usr/bin/docker compose -f compose.prod.yml --env-file .env down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable <portal>.service
sudo systemctl start <portal>.service
```

## 9. Email via SES

Platform rule:

- Keep SMTP/SES credentials in environment variables.
- Keep non-secret email defaults in portal config ini.

Validate from running app container:

```bash
docker compose -f compose.prod.yml --env-file .env exec app python marco/manage.py shell -c "from django.core.mail import send_mail; send_mail('test','ok','noreply@example.com',['you@example.com'])"
```

## 10. Backups

### 10.1 Principles

- Use EBS snapshots for volume-level recovery.
- Use logical PostgreSQL dumps for portability and point-in-time rollback.
- Keep backup jobs in the portal repo where operational ownership lives.

### 10.2 Cron pattern

Use portal-owned scripts and portal-owned paths:

```cron
# DB dump + retention
15 2 * * * cd /home/ubuntu/portals/<portal> && /bin/bash -lc './scripts/db_dump.sh -c ./docker/compose.prod.yml -e ./docker/.env -d ./docker/backups/sql && find ./docker/backups/sql -type f -name "*.sql" -mtime +10 -delete' >> /home/ubuntu/portals/<portal>/docker/backups/db_dump.log 2>&1
```

Add portal-specific snapshot/refresh jobs in the portal runbook.

## 11. Release and rollback pattern

### 11.1 Deployment flow

```bash
cd /home/ubuntu/portals/<portal>/docker

docker compose -f compose.prod.yml --env-file .env pull
docker compose -f compose.prod.yml --env-file .env up -d
```

Rollback is the same flow after resetting image tag(s) in `.env` to a known-good value.

### 11.2 Decision table

| Change type | Rebuild base image | Rebuild overlay image | Host action |
|---|---:|---:|---|
| Portal templates/static/settings | no | yes | Pull new overlay tag, recreate app |
| Portal `.env` change | no | no | Recreate relevant service |
| Portal config ini change | no | no | Recreate app |
| Shared app/library change | yes | yes | Rebuild base, then overlay, then pull/recreate |
| Core framework/runtime dependency | yes | yes | Rebuild base, then overlay, then pull/recreate |
| Compose config change only | no | no | Run compose up -d |

## 12. Multiple portals on one host

Supported when sized correctly.

Rules:

- Unique `COMPOSE_PROJECT_NAME` per portal.
- Non-overlapping host ports.
- Separate systemd units.
- Separate Nginx server blocks.
- Separate static/media/backups paths.

If combined service load becomes memory/CPU constrained, split portals to separate instances.

## 13. Next step

After host setup is complete, follow the target portal's runbook for:

- Portal artifact placement.
- Portal `.env` values.
- Portal config ini selection.
- Portal-specific services and routes.
- Portal-specific backup jobs.
