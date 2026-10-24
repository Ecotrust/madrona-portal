# AWS Host Setup - Madrona Portal Platform

This guide prepares an AWS server to run Madrona portals. 

## Images

Madrona uses two kinds of Docker images:

* The **shared base image** contains software used by all portals.
* Each **portal image** adds one portal's application and settings to the shared image.

Please note:  

* On an AWS server, you run the portal image, not the shared image by itself.
* Rebuilding the shared image does not update a running portal. 
* When shared software changes, rebuild the shared image, then rebuild and deploy each affected portal image.
* For production, use a fixed Git commit tag for both images so deployments are repeatable. 
* Reserve `latest` for development and testing.

## Prerequisites

* AWS account with EC2 permissions
* GitHub access to required container packages
* Domain and DNS control for TLS setup
* SSH client and private key management process

## GHCR setup (one-time)

### CI push permissions

If you run into permissions issues for CI workflows, ensure your workflows can publish images and can write packages in GHCR.

### Host pull permissions

Create a read-only token for deployment hosts to pull container images. Store it in host secret storage and run login on-host:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

### Verify image availability

Before host rollout, confirm the target image tags exist:

```bash
docker manifest inspect ghcr.io/<org>/<portal-image>:<image-tag> >/dev/null
```

## AWS infrastructure baseline

### EC2

- Recommended baseline for app + db + redis only: `t3.medium`.
- Increase instance class when portal images include extra services (search engines, catalog systems, app servers).
- Start with at least 40-60 GB gp3 root volume for logs, images, and backups.

### Security group

Allow inbound as needed:

- `22/tcp` from restricted admin CIDRs.
- `80/tcp` and `443/tcp` from internet.

### Elastic IP

Associate an Elastic IP for stable DNS mapping and easier cutovers.

## Ubuntu server setup

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

Recommended host hardening:

- Enable unattended upgrades.
- Add swap for memory pressure protection.
- Install baseline monitoring (for example Munin or CloudWatch agent).

## Host layout for portal repos

Use one directory per portal checkout:

```text
/home/ubuntu/portals/
  portal-a/
  portal-b/
```

Each portal directory should contain:

- Portal compose files
- Portal `.env` file (copy using `.env.example`)
- Portal production config ini file(s)
- Portal static/media/backups directories as needed

## Nginx and TLS pattern

### Install and obtain certificates

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Try using a an existing portal Nginx configuration as a template. If you don't have an existing configuration, here is a basic server block for the portal domain:  

```nginx
server {
    listen 80;
    server_name portal.example.org www.portal.example.org;
    
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

You can test Nginx config with `sudo nginx -t`

Reload Nginx and obtain TLS certificates with Certbot.

```bash
sudo service nginx restart
# alternatively with systemctl
# sudo systemctl reload nginx
sudo certbot --nginx -d <portal-domain> -d <optional-www-domain>
```

## Email via SES

Platform guidance:

- Store SMTP/SES credentials in environment (`.env`) variables.
- Keep non-secret email defaults in portal config ini.

Validate from running app container:

```bash
docker compose -f compose.prod.yml --env-file .env exec app python marco/manage.py shell -c "from django.core.mail import send_mail; send_mail('test','ok','noreply@example.com',['you@example.com'])"
```

## Backups

### Principles

- Use EBS snapshots for volume-level recovery.
- Use logical PostgreSQL dumps for portability and point-in-time rollback.
- Keep backup jobs in the portal repo where operational ownership lives.

### Cron pattern

Use portal-owned scripts and portal-owned paths:

```cron
# DB dump + retention
15 2 * * * cd /home/ubuntu/portals/<portal> && /bin/bash -lc './scripts/db_dump.sh -c ./docker/compose.prod.yml -e ./docker/.env -d ./docker/backups/sql && find ./docker/backups/sql -type f -name "*.sql" -mtime +10 -delete' >> /home/ubuntu/portals/<portal>/docker/backups/db_dump.log 2>&1
```

Add portal-specific snapshot/refresh jobs in the portal runbook.

## Release and rollback pattern

### Release Deployment

```bash
cd /home/ubuntu/portals/<portal>/docker

docker compose -f compose.prod.yml --env-file .env pull
docker compose -f compose.prod.yml --env-file .env up -d
```

### Rollback 

To rollback, first update the image tag in the `.env`: 

```bash
vim /home/ubuntu/portals/<portal>/docker/.env
```

Then follow the same steps as a release deployment: 

```bash
docker compose -f compose.prod.yml --env-file .env pull
docker compose -f compose.prod.yml --env-file .env up -d
```


### Decision table

| Change type | Rebuild base image | Rebuild overlay image | Host action |
|---|---:|---:|---|
| Portal templates/static/settings | no | yes | Pull new overlay tag, recreate app |
| Portal `.env` change | no | no | Recreate relevant service |
| Portal config ini change | no | no | Recreate app |
| Shared app/library change (*e.g.*, mp-\*, madrona-\*) | yes | yes | Rebuild base, then overlay, then pull/recreate |
| Core framework/runtime dependency | yes | yes | Rebuild base, then overlay, then pull/recreate |
| Compose config change only | no | no | Run compose up -d |

## Multiple portals on one host

Dependencies:

- Unique `COMPOSE_PROJECT_NAME` per portal.
- Non-overlapping host ports.
- Separate systemd units.
- Separate Nginx server blocks.
- Separate static/media/backups paths.

## Next step

After host setup is complete, follow the target portal's runbook for:

- Portal artifact placement.
- Portal `.env` values.
- Portal config ini selection.
- Portal-specific services and routes.
- Portal-specific backup jobs.
