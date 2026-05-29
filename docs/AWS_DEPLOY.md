# AWS Deployment Guide — Madrona Portal (WCOA)

This guide takes you from a blank AWS account to a running production stack.
All services (Django, PostGIS, Redis, Elasticsearch, Geoportal) run as Docker
containers on a single EC2 instance using Docker Compose.

The Docker image is built by GitHub Actions and stored in the GitHub Container
Registry (GHCR). The EC2 server pulls a pre-built image — no source code
checkout or build step is needed on the server.

---

## Prerequisites

- An AWS account with billing enabled
- SSH client on your local machine
- A GitHub account with admin access to the `Ecotrust` organization

---

## Phase 0 — One-time GHCR Setup

These steps are done once by a GitHub org admin. Skip to Phase 1 if the
`madrona-portal` package already exists in GHCR.

### 0.1 Create a PAT for GitHub Actions (CI push)

This token lets GitHub Actions push images to GHCR on behalf of the org.

**GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**

| Setting | Value |
|---|---|
| Token name | `madrona-portal-ci` |
| Expiration | 1 year (set a reminder to rotate) |
| Resource owner | `Ecotrust` |
| Repository access | All repositories (needed to read all sub-app repos) |
| Permissions → Contents | Read-only |
| Permissions → Packages | Read and write |

Copy the token. Add it as an Actions secret in `madrona-portal`:

**GitHub → `Ecotrust/madrona-portal` → Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `GH_PAT` | `<paste token>` |

### 0.2 Create a read-only PAT for the EC2 server (pull only)

**GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**

| Setting | Value |
|---|---|
| Token name | `madrona-portal-ec2` |
| Expiration | 1 year |
| Resource owner | `Ecotrust` |
| Repository access | Public repositories only |
| Permissions → Packages | Read-only |

Copy this token — you will add it to the server `.env` in Phase 4.

### 0.3 Trigger the first image build

Push a commit to the `docker` branch of `madrona-portal`, or run the workflow
manually:

**GitHub → `Ecotrust/madrona-portal` → Actions → "Build and Push to GHCR" → Run workflow**

The first build takes 15–25 minutes (compiling GDAL, installing all Python
packages). Subsequent builds are faster thanks to GitHub Actions layer caching.

Confirm the image appears at:
**GitHub → `Ecotrust` org → Packages → `madrona-portal`**

Note the short SHA from the workflow summary — you can use it to pin a specific
build on EC2 instead of always pulling `:latest`.

---

## Phase 1 — AWS Infrastructure

### 1.1 Create a key pair

**AWS Console → EC2 → Key Pairs → Create key pair**

| Setting | Value |
|---|---|
| Name | `madrona-portal` |
| Key pair type | RSA |
| Private key format | `.pem` (Linux/Mac) or `.ppk` (PuTTY/Windows) |

Download the `.pem` file and move it somewhere safe:

```bash
mv ~/Downloads/madrona-portal.pem ~/.ssh/
chmod 400 ~/.ssh/madrona-portal.pem
```

### 1.2 Create a security group

**AWS Console → EC2 → Security Groups → Create security group**

| Setting | Value |
|---|---|
| Name | `madrona-portal-sg` |
| Description | Madrona Portal web server |
| VPC | Default VPC (or your own) |

**Inbound rules:**

| Type | Port | Source | Purpose |
|---|---|---|---|
| SSH | 22 | Your IP only (`x.x.x.x/32`) | Server access |
| HTTP | 80 | `0.0.0.0/0` | Web traffic (Nginx) |
| HTTPS | 443 | `0.0.0.0/0` | Web traffic (Nginx + SSL) |

> Do **not** open port 8000 to the public. Nginx proxies traffic to Gunicorn
> on port 8000 internally.

**Outbound rules:** leave the default (all traffic allowed).

### 1.3 Launch an EC2 instance

**AWS Console → EC2 → Instances → Launch instances**

| Setting | Value |
|---|---|
| Name | `madrona-portal` |
| AMI | Ubuntu Server 24.04 LTS (64-bit x86) |
| Instance type | `t3.large` (8 GB RAM) — minimum. See note below. |
| Key pair | `madrona-portal` (created above) |
| Security group | `madrona-portal-sg` (created above) |
| Storage | 60 GB gp3 — expand the default 8 GB root volume |

> **Why t3.large?** Elasticsearch alone reserves 1 GB of heap
> (`-Xms512m -Xmx512m`) plus JVM overhead. Add PostGIS, Gunicorn workers,
> Redis, and Tomcat (Geoportal) and you need at least 6–7 GB free. A
> `t3.large` (8 GB) is the practical minimum; `t3.xlarge` (16 GB) gives
> comfortable headroom.

> **Why 60 GB?** The Docker image is ~3–4 GB after pull. PostGIS data,
> Elasticsearch indices, and Docker's image cache add up quickly.

Launch the instance and wait for it to reach **Running** state.

### 1.4 Allocate an Elastic IP

Without an Elastic IP, AWS reassigns your public IP every time the instance
stops. An Elastic IP is free while attached to a running instance.

**AWS Console → EC2 → Elastic IPs → Allocate Elastic IP address**

- Click **Allocate**
- Select the new IP → **Actions → Associate Elastic IP address**
- Choose your `madrona-portal` instance → **Associate**

Note the Elastic IP — you will use it in your `.env` and DNS records.

---

## Phase 2 — Server Setup

### 2.1 SSH into the instance

```bash
ssh -i ~/.ssh/madrona-portal.pem ubuntu@<ELASTIC_IP>
```

### 2.2 Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Install Docker Engine

AWS's Ubuntu AMI does not include Docker. Install the official Docker Engine
(not the snap package — it has permission issues with volumes).

```bash
# Add Docker's official GPG key
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

# Install Docker Engine + Compose plugin + BuildKit
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

*Verify Docker is running:*

```bash
sudo systemctl status docker

# if not running, start the service
sudo systemctl start docker
```

### 2.4 Allow your user to run Docker without sudo

```bash
sudo usermod -aG docker ubuntu
newgrp docker          # apply without logging out
docker run hello-world # verify
```

### 2.5 Enable Docker to start on boot

```bash
sudo systemctl enable docker
sudo systemctl enable containerd
```

### 2.6 Log in to GitHub Container Registry

```bash
# You will add GHCR_PAT to .env in Phase 4.
# Run this now using the read-only PAT you created in Phase 0.2:
echo "<your-ec2-read-only-pat>" | docker login ghcr.io -u <your-github-username> --password-stdin
```

The login token is saved to `~/.docker/config.json` and persists across
reboots. You only need to re-run this if the PAT expires.

---

## Phase 3 — Transfer Geoportal WAR Files

The Geoportal service requires two Java WAR files that are not in any Git
repository. Copy them from the old production server.

**On the old server**, find the WAR files:

```bash
# Common locations on the old server:
find / -name "geoportal.war" -o -name "harvester.war" 2>/dev/null
```

**On your local machine**, SCP them to the new EC2 instance:

```bash
# Replace OLD_SERVER_IP and paths as appropriate
scp ubuntu@<OLD_SERVER_IP>:/path/to/geoportal.war \
    ubuntu@<ELASTIC_IP>:/tmp/geoportal.war

scp ubuntu@<OLD_SERVER_IP>:/path/to/harvester.war \
    ubuntu@<ELASTIC_IP>:/tmp/harvester.war
```

---

## Phase 4 — Clone the Portal Configuration

The EC2 server only needs the `madrona-portal` repository — for the Compose
file, Nginx templates, entrypoint scripts, and environment configuration.
No sub-app repos are needed; all application code is baked into the image.

### 4.1 Set up SSH access to GitHub (on the server)

```bash
ssh-keygen -t ed25519 -C "madrona-portal-server" -f ~/.ssh/github -N ""
cat ~/.ssh/github.pub
```

Copy the output and add it as a **Deploy Key** in `madrona-portal`:

**GitHub → `Ecotrust/madrona-portal` → Settings → Deploy keys → Add deploy key**
- Title: `madrona-portal EC2`
- Paste the public key
- Allow write access: No

Configure SSH to use this key:

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    IdentityFile ~/.ssh/github
    StrictHostKeyChecking no
EOF
```

### 4.2 Clone madrona-portal

```bash
mkdir ~/portals && cd ~/portals
git clone -b docker git@github.com:Ecotrust/madrona-portal.git madrona-portal
```

Verify:

```bash
ls ~/portals/
# madrona-portal/
```

### 4.3 Move the WAR files into place

**On the new EC2 instance**, move them into the expected location:

```bash
mv /tmp/geoportal.war ~/portals/madrona-portal/docker/wars/
mv /tmp/harvester.war ~/portals/madrona-portal/docker/wars/
```

The `.env.example` defaults point to `./wars/geoportal.war` and
`./wars/harvester.war` (relative to the `docker/` directory), so these paths
will work without any further changes.

---

## Phase 5 — Configure the Environment

### 5.1 Create the `.env` file

```bash
cd ~/portals/madrona-portal
cp docker/.env.example docker/.env
```

### 5.2 Generate a secret key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5.3 Edit `.env`

```bash
nano docker/.env
```

Set these values at minimum:

```ini
# Environment
DJANGO_ENV=production

# Gunicorn workers (2× vCPU count; t3.large has 2 vCPUs → 4 workers)
GUNICORN_WORKERS=4

# GHCR — the read-only PAT from Phase 0.2 (documents what token was used to
# log in; docker login stores credentials in ~/.docker/config.json)
GHCR_PAT=<your-ec2-read-only-pat>

# Django
SECRET_KEY=<paste generated key here>
ALLOWED_HOSTS=<ELASTIC_IP>,localhost
DEBUG=False

# Database
DB_PASSWORD=<strong random password>

# Redis
REDIS_PASSWORD=<strong random password>

# Superuser (created automatically on first boot if DB_INIT=1)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=your@email.com
DJANGO_SUPERUSER_PASSWORD=<strong password>
```

Can be added now or later:  

```ini
# Password for the 'elastic' user
ELASTIC_PASSWORD=<see 1password>

# Password for the 'kibana_system' user
KIBANA_PASSWORD=<see 1password>

# Admin User (Full Access)
gpt_admin_username=<see 1password>
gpt_admin_password=<see 1password>

# Publisher User (Can publish metadata)
gpt_publisher_username=<see 1password>
gpt_publisher_password=<see 1password>  

# Regular User (Read-only access)
gpt_user_username=<see 1password>
gpt_user_password=<see 1password>

gpt_wcoa_username=<see 1password>
gpt_wcoa_password=<see 1password>

gpt_esri_username=<see 1password>
gpt_esri_password=<see 1password>

gpt_frame_options=DENY
gpt_allowed_origin="localhost localhost:* <ELASTIC_IP> <portal URLs>"
```

Leave everything else at its default for now. You can add email, OAuth, and
Elasticsearch credentials later.

### 5.4 Create the ini config file

```bash
cd ~/portals/madrona-portal/marco
cp config.docker.ini.template config.wcoa.docker.ini
```

---

## Phase 6 — Pull and Start the Stack

### 6.1 Pull the image from GHCR

```bash
docker pull ghcr.io/ecotrust/madrona-portal:latest
```

> To use a specific build instead of `latest`, note the short SHA from the
> GitHub Actions workflow summary and pull by tag:
> `docker pull ghcr.io/ecotrust/madrona-portal:abc1234`

### 6.2 Start the stack

:warning: For a fresh database, run with `DB_INIT=1` the first time to load initial fixtures and create the superuser:**
```bash
cd ~/portals/madrona-portal/docker

DB_INIT=1 docker compose -f docker-compose.prod.yml up -d
```
*On subsequent starts, leave `DB_INIT` at its default (`0`) to skip the fixture and superuser steps.*

For an existing database:

```bash
cd ~/portals/madrona-portal/docker

docker compose -f docker-compose.prod.yml up -d
```

### 6.3 Watch the startup logs

```bash
docker compose -f docker-compose.prod.yml logs -f app
```

On first boot the entrypoint automatically:
1. Waits for PostgreSQL to be healthy
2. Runs `collectstatic` and `compress` (always)
3. Runs `migrate` (only when `DB_INIT=1`)
4. Detects fresh database → loads initial fixtures (only when `DB_INIT=1`)
5. Creates the superuser from `.env` (only when `DB_INIT=1`)
6. Starts Gunicorn

Startup takes 2–5 minutes. Look for `Booting worker` lines from Gunicorn.

> For a fresh database, run with `DB_INIT=1` the first time:
> ```bash
> DB_INIT=1 docker compose -f docker/docker-compose.prod.yml up -d
> ```
> On subsequent starts, leave `DB_INIT` at its default (`0`) to skip the
> fixture and superuser steps.

### Apply migrations (if needed)

```bash
docker compose -f docker/docker-compose.prod.yml exec app python marco/manage.py migrate
```

### Import database

Copy your SQL dump to the server (e.g., using `scp`):

```bash
scp /path/to/your_dump.sql ubuntu@<ELASTIC_IP>:/home/ubuntu/your_dump.sql
```

From `madrona-portal/docker`:
```bash
../scripts/db-restore.sh --drop <path_to_your_sql>
```
*example:*
```bash
../scripts/db-restore.sh --drop ../../madrona-apps/wcoa/wcodp_prod_dump_20260320.sql
```

### Apply migrations again (if needed)

```bash
docker compose -f docker/docker-compose.prod.yml exec app python marco/manage.py migrate
```

### Migration to Layers

```bash
docker compose -f docker/docker-compose.prod.yml exec app python marco/manage.py migration_to_layers
```



### Collect static and compress assets

Static files are collected automatically on every container startup. To force
a manual re-run without restarting the container:

```bash
docker compose -f docker/docker-compose.prod.yml exec app python marco/manage.py collectstatic --noinput
docker compose -f docker/docker-compose.prod.yml exec app python marco/manage.py compress
```

### Smoke test

```bash
curl -I http://localhost:8000/
# Expected: HTTP/1.1 200 OK  (or 301/302 redirect)
```

If you get a connection refused, the app is still starting. Wait 30 seconds
and try again.

---

## Phase 7 — Nginx + SSL (Production Hardening)

Gunicorn should not be exposed directly to the internet. Nginx handles SSL termination, compression, and static file serving.

### 7.1 Install Nginx and Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 7.2 Create a DNS A record

In your DNS provider (Route 53, Cloudflare, etc.):

| Type | Name | Value |
|---|---|---|
| A | `portal.westcoastoceans.org` | `<ELASTIC_IP>` |

Wait for DNS to propagate before continuing:

```bash
dig portal.westcoastoceans.org
# Should return your Elastic IP
```

### 7.3 Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/madrona-portal
```

Paste:

```nginx
server {
    listen 80;
    server_name <portal.westcoastoceans.org> or <ELASTIC_IP>;

    access_log /var/log/nginx/wcoa.access.log;
    error_log /var/log/nginx/wcoa.error.log;

    location /static/ {
        alias /home/ubuntu/portals/madrona-portal/docker/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /home/ubuntu/portals/madrona-portal/docker/media/;
    }

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        client_max_body_size 50M;
    }

    location /geospatial/ {
        alias /var/www/html/geospatial/;
        autoindex on;
    }

    location /munin/static/ {
        alias /etc/munin/static/;
    }

    location /munin {
        alias /var/cache/munin/www;
    }

    location /nativeland {
        proxy_pass https://native-land.ca/;
        resolver 8.8.8.8;
        resolver_timeout 10s;
        proxy_redirect off;
        proxy_pass_request_headers on;
        proxy_ssl_server_name on;
    }

    # Shared CORS policy for these proxied endpoints
    # (if you only want specific origins, replace "*" with your domain)
    set $cors_allow_origin "*";

    location ~ ^/(?:_search/|_doc/|metadata).*$ {
        proxy_pass http://127.0.0.1:9200;
        proxy_redirect off;
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        add_header Access-Control-Allow-Origin $cors_allow_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;

        if ($request_method = OPTIONS) {
            add_header Access-Control-Max-Age 1728000 always;
            add_header Content-Type "text/plain; charset=utf-8" always;
            add_header Content-Length 0 always;
            return 204;
        }
    }

    location ~ ^/(?:manager|host-manager|semantix|solr|gc|geoportal|harvester).*$ {
        proxy_pass http://<ELASTIC_IP>:8080;
        proxy_redirect off;
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        add_header Access-Control-Allow-Origin $cors_allow_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;

        if ($request_method = OPTIONS) {
            add_header Access-Control-Max-Age 1728000 always;
            add_header Content-Type "text/plain; charset=utf-8" always;
            add_header Content-Length 0 always;
            return 204;
        }
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/madrona-portal \
           /etc/nginx/sites-enabled/madrona-portal
sudo nginx -t          # verify config
sudo systemctl restart nginx
```

> **Static file permissions:** Nginx runs as `www-data`, which must be able to
> traverse every directory in the path to `docker/static/`. Ubuntu home
> directories default to `750` (group-only execute), which blocks `www-data`.
> Fix it once after cloning:
>
> ```bash
> chmod o+x /home/ubuntu
> ```
>
> Verify with `namei -l /home/ubuntu/portals/madrona-portal/docker/static/` —
> every component in the path needs at least `o+x`.

### 7.4 Obtain an SSL certificate

```bash
sudo certbot --nginx -d <URL>
```

Certbot edits your Nginx config automatically to add SSL and redirect HTTP
to HTTPS. It installs a cron job to renew the certificate automatically.

### 7.5 Update `ALLOWED_HOSTS`

Add the domain to `docker/.env`:

```ini
ALLOWED_HOSTS=portal.westcoastoceans.org,<ELASTIC_IP>,localhost
```

Restart the app container to pick up the change:

```bash
cd ~/portals/madrona-portal
docker compose -f docker/docker-compose.prod.yml up -d --force-recreate app
```

---

## Import media

#### Copy the media files
```bash
scp -r {your_media_dir} ubuntu@<your_server_ip>:/home/ubuntu/portals/madrona-portal/docker/media/
```

#### Create a directory for data_manager
```bash
mkdir ~/portals/madrona-portal/docker/data_manager
```

## Migrate existing GeoPortal records

1. Update .env with the reindex remote whitelist and port. You can find this info by looking at the old server's configuration or by asking the previous admin.

2. Edit the hosts file to allow the server to resolve the old Elastic IP of the GeoPortal instance to the new internal Docker network:

```bash
sudo vim /etc/hosts
# Add the following line, replacing <OLD_ELASTIC_IP> and <ES_REINDEX_REMOTE_WHITELIST from .env>:
<OLD_IP> <ES_REINDEX_REMOTE_WHITELIST from .env>
```

3. Ensure the app is running, you can migrate existing GeoPortal records with the following command (replace the username and password):

```bash
time curl -X POST "http://localhost:9200/_reindex"  -H 'Content-Type: application/json' -d'{"conflicts": "proceed", "max_docs": 51000, "source": {"remote": { "host":"http://[ES_REINDEX_REMOTE_WHITELIST]:80/geoportal/elastic/", "username": "[[USERNAME]]", "password": "[[PASSWORD]]"  }, "index": "metadata", "size": 100 }, "dest": { "index": "metadata" } }'
```

4. Do a down, including volumes, and up for the elasticsearch container and geoportal to pick up the new records:

```bash
docker compose -f docker/docker-compose.prod.yml down elastic geoportal -v
docker compose -f docker/docker-compose.prod.yml up -d elastic geoportal
```

---

## Phase 8 — Keep the Stack Running Across Reboots

### 8.1 Create a systemd service

```bash
sudo nano /etc/systemd/system/madrona-portal.service
```

Paste:

```ini
[Unit]
Description=Madrona Portal Docker Compose Stack
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/portals/madrona-portal
ExecStart=/usr/bin/docker compose \
    -f docker/docker-compose.prod.yml \
    --env-file docker/.env \
    up -d
ExecStop=/usr/bin/docker compose \
    -f docker/docker-compose.prod.yml \
    --env-file docker/.env \
    down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

### 8.2 Enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable madrona-portal
```

### 8.3 Test it (simulates a reboot)

```bash
sudo systemctl stop madrona-portal
sudo systemctl start madrona-portal
docker compose -f docker/docker-compose.prod.yml ps    # all services should show "running"
```

---

## AWS Email (SES) Setup

### Verify your domain in AWS SES (Simple Email Service)

1. Go to SES Console → us-west-2 → Create identity → choose Domain → enter:
`portal.westcoastoceans.org`
2. Leave defaults
3. Click "Create identity"

### Add the provided DNS records to your DNS provider
1. In the SES Console, click on your new identity → DNS records tab
2. Add the provided records to your DNS provider (e.g., Hover)
3. Wait for AWS to verify the domain (minute to hours)

### Create SMTP Credentials
1. In SES Console → SMTP Settings → Create SMTP credentials → note the username and password (only shown once).

### Update the portal configuration
1. SSH into the server
2. Open the `.env` file
3. Add the following values (replace with your SMTP credentials):
```
EMAIL_HOST=email-smtp.us-west-2.amazonaws.com
EMAIL_PORT=587
EMAIL_HOST_USER=<smtp username from step 4>
EMAIL_HOST_PASSWORD=<smtp password from step 4>
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=noreply@prod.mail.ecotrust.org
```

### Create custom mail from domain
1. In SES Console → Identities → click on your domain → Create mail from domain
2. Enter a subdomain (e.g., `mail`) → Create
3. Add the provided DNS records to your DNS provider
4. Wait for AWS to verify the mail from domain

### Request SES production access
Submit a production access request in SES Console → Account dashboard → Request production access. Takes 24hrs typically.

---  

## Automatic Security Updates

Install unattended-upgrades and update-notifier-common to automatically apply security updates to the server OS:
```bash
sudo apt install unattended-upgrades update-notifier-common -y
```

Enable automatic updates:
```bash
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Edit the configuration to allow automatic reboots and set the time for reboots to occur:
```bash
// Open the config file
sudo vim /etc/apt/apt.conf.d/50unattended-upgrades

// Find, uncomment, and set "true" the line that contains "Unattended-Upgrade::Automatic-Reboot"
Unattended-Upgrade::Automatic-Reboot "true";

// Find and uncomment the line that contains "Unattended-Upgrade::Automatic-Reboot-Time"
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
```

---  

## Install Munin

```bash
sudo apt install munin -y
```

---

## Set Up Swap Space

```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---  

## Add Google Analytics Key
1. Get the GA tracking ID (e.g., `G-XXXXXXXXXX`)
2. SSH into the server and edit the `.env` file
3. Edit or add the following line in the `.env` file:
```bash
GA_ACCOUNT=G-XXXXXXXXXX
```

---

## Deploying a New Release

When code changes are merged to the `docker` branch, GitHub Actions
automatically builds and pushes a new image to GHCR. To deploy it:


### On the server

```bash
cd ~/portals/madrona-portal

# Pull the latest image (or a specific SHA tag for a pinned deploy)
docker pull ghcr.io/ecotrust/madrona-portal:latest

# Recreate only the app container — db, Redis, and Elasticsearch are untouched
docker compose -f docker/docker-compose.prod.yml up -d --force-recreate app
```

Downtime is limited to the container restart (~5–10 seconds).

### Rolling back to a previous build

```bash
# List available tags in GHCR (or check the GitHub Actions workflow summaries
# for the SHA of any previous build)

# Pull the specific SHA tag
docker pull ghcr.io/ecotrust/madrona-portal:<previous-sha>

# Update IMAGE_TAG in docker/.env, then recreate:
# IMAGE_TAG=<previous-sha> in docker/.env
docker compose -f docker/docker-compose.prod.yml up -d --force-recreate app
```

### If portal configuration changes (config.wcoa.docker.ini)

The ini file is bind-mounted into the container (read-only), so changes take effect immediately on the next container restart — no image rebuild needed:

```bash
nano ~/portals/madrona-portal/marco/config.wcoa.docker.ini
docker compose -f docker/docker-compose.prod.yml up -d --force-recreate app
```

---

## Useful Commands (on the server)

All `docker compose` commands run from `~/portals/madrona-portal/`.

```bash
# Tail app logs
docker compose -f docker/docker-compose.prod.yml logs -f app

# Run a Django management command
docker compose -f docker/docker-compose.prod.yml --env-file docker/.env run --rm app python marco/manage.py <command>

# Open a Django shell
docker compose -f docker/docker-compose.prod.yml --env-file docker/.env run --rm app python marco/manage.py shell

# Open a database shell
docker exec -it \
    $(docker compose -f docker/docker-compose.prod.yml --env-file docker/.env ps -q db) \
    psql -U postgres wcoa_docker_db

# Check disk and Docker space usage
df -h
docker system df

# Remove old/unused images to free space
docker image prune -f

# Stop the stack (data preserved in named volumes)
docker compose -f docker/docker-compose.prod.yml --env-file docker/.env down

# Full reset — DESTROYS ALL DATA
docker compose -f docker/docker-compose.prod.yml --env-file docker/.env down -v
```

---

## Services and Ports

| Service | Image | Internal port | Notes |
|---|---|---|---|
| `app` | `ghcr.io/ecotrust/madrona-portal:latest` | 8000 | Proxied by Nginx |
| `db` | `postgis/postgis:16-3.4` | 5432 | Restrict in security group after go-live |
| `tasks` | `redis:7-alpine` | 6379 | Restrict in security group after go-live |
| `geoportal` | `tomcat:9-jdk11` | 8080 | Add Nginx location if public access needed |
| `elastic` | `elasticsearch:8.19.12` | 9200, 9300 | Restrict in security group after go-live |

> After go-live, update your security group inbound rules to remove public
> access to ports 5432, 6379, 9200, and 9300. These ports are only needed
> internally between containers on `madronanetwork`.
