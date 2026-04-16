# AWS Deployment Guide — Madrona Portal (WCOA)

This guide takes you from a blank AWS account to a running production stack.
All services (Django, PostGIS, Redis, Elasticsearch, Geoportal) run as Docker
containers on a single EC2 instance using Docker Compose.

---

## Prerequisites

- An AWS account with billing enabled
- Your local machine has the AWS CLI installed and configured,
  or you are comfortable using the AWS Console
- SSH client on your local machine
- A GitHub account with access to all required repos

---

## Phase 1 — AWS Infrastructure

### 1.1 Create a key pair

You need this before launching the instance.

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

> Do **not** open port 8000 to the public. Nginx (added in Phase 5) will
> proxy traffic to gunicorn on port 8000 internally.

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
> (`-Xms512m -Xmx512m` in docker-compose.yml) plus JVM overhead.
> Add PostGIS, gunicorn workers, Redis, and Tomcat (Geoportal) and you need
> at least 6–7 GB free. A `t3.large` (8 GB) is the practical minimum;
> `t3.xlarge` (16 GB) gives comfortable headroom.

> **Why 60 GB?** The Docker image is ~3–4 GB after build. PostGIS data,
> Elasticsearch indices, and Docker's build cache add up quickly.

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
sudo apt-get update && sudo apt-get upgrade -y
```

### 2.3 Install Docker Engine

AWS's Ubuntu AMI does not include Docker. Install the official Docker Engine
(not the snap package — it has permission issues with volumes).

```bash
# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the Docker apt repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin + BuildKit
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
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

---

## Phase 3 — Clone the Repositories

The Dockerfile build context must be the **workspace root** — a parent
directory containing both `madrona-portal/` and `madrona-apps/` as siblings.
This layout is required; it is not optional.

### 3.1 Set up SSH access to GitHub (on the server)

```bash
ssh-keygen -t ed25519 -C "madrona-portal-server" -f ~/.ssh/github -N ""
cat ~/.ssh/github.pub
```

Copy the output and add it as a **Deploy Key** in each GitHub repository
(or as an SSH key on your GitHub account if you have access to all repos):

**GitHub repo → Settings → Deploy keys → Add deploy key**
- Paste the public key
- Title: `madrona-portal EC2`
- Enable "Allow write access": No (read-only is sufficient)

Configure SSH to use this key for GitHub:

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    IdentityFile ~/.ssh/github
    StrictHostKeyChecking no
EOF
```

### 3.2 Create the workspace and clone

```bash
mkdir ~/portals && cd ~/portals
```

Clone the main portal:

```bash
git clone -b docker git@github.com:Ecotrust/madrona-portal.git madrona-portal
```

Clone all sub-apps:

```bash
mkdir madrona-apps && cd madrona-apps

git clone git@github.com:Ecotrust/django_url_shortener.git
git clone git@github.com:Ecotrust/madrona-analysistools.git
git clone git@github.com:Ecotrust/madrona-features.git
git clone git@github.com:Ecotrust/madrona-manipulators.git
git clone git@github.com:Ecotrust/madrona-scenarios.git
git clone git@github.com:Ecotrust/mp-accounts.git
git clone git@github.com:Ecotrust/mp-data-manager.git
git clone git@github.com:Ecotrust/mp-drawing.git
git clone git@github.com:Ecotrust/mp-explore.git
git clone git@github.com:Ecotrust/mp-layers.git
git clone git@github.com:Ecotrust/mp-map-groups.git
git clone git@github.com:Ecotrust/mp-proxy.git
git clone git@github.com:Ecotrust/mp-visualize.git
git clone git@github.com:Ecotrust/p97-nursery.git
git clone -b vagrant2docker git@github.com:Ecotrust/wcoa.git

cd ..
```

Verify the layout:

```bash
ls ~/portals/
# madrona-portal/  madrona-apps/
```

---

## Phase 4 — Configure the Environment

### 4.1 Create the `.env` file

```bash
cd ~/portals/madrona-portal
cp .env.example .env
```

### 4.2 Generate a secret key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the output — you will paste it as `SECRET_KEY` below.

### 4.3 Edit `.env`

```bash
nano .env
```

Set these values at minimum:

```ini
# Django
SECRET_KEY=<paste generated key here>
ALLOWED_HOSTS=<ELASTIC_IP>,localhost
DEBUG=False
DJANGO_ENV=production

# Database
DB_PASSWORD=<strong random password>

# Redis
REDIS_PASSWORD=<strong random password>

# Superuser (created automatically on first boot)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=your@email.com
DJANGO_SUPERUSER_PASSWORD=<strong password>

# Gunicorn workers (set to 2× vCPU count; t3.large has 2 vCPUs → 4 workers)
GUNICORN_WORKERS=4
```

Leave everything else at its default for now. You can add email, OAuth, and
Elasticsearch credentials later.

### 4.4 Create ini file 

```bash
cd ~/portals/madrona-portal/marco
cp config.docker.ini.template config.wcoa.docker.ini
```


---

## Phase 5 — Build the Docker Image

> **Important:** The `--builder desktop-linux` flag in the local development
> guide is specific to Docker Desktop on Mac. On Linux EC2 you omit it —
> BuildKit is the default builder.

From the **workspace root** (`~/portals/`):

```bash
cd ~/portals

docker buildx build \
    --load \
    -f madrona-portal/docker/Dockerfile \
    -t madrona-portal-app:latest \
    .
```

This will take 10–20 minutes on first build (compiling GDAL, installing all
Python packages). Subsequent builds are fast thanks to layer caching.

Watch for any errors. Common first-build issues:
- Out of disk space → increase EBS volume or run `docker system prune -f` first
- Network timeouts fetching packages → re-run the command (layer cache resumes)

---

## Phase 6 — Start the Stack

From `~/portals/madrona-portal/`:

```bash
cd ~/portals/madrona-portal

docker compose -f docker/docker-compose.yml \
    --env-file .env \
    --profile full \
    up -d
```

### 6.1 Watch the startup logs

```bash
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    logs -f app
```

On first boot the entrypoint automatically:
1. Waits for PostgreSQL
2. Runs `migrate`
3. Runs `collectstatic` and `compress`
4. Detects fresh database → loads initial fixtures
5. Creates the superuser from `.env`
6. Starts gunicorn (because `DEBUG=False`)

Startup takes 2–5 minutes. You should see `Booting worker` lines from
gunicorn when it is ready.

### 6.2 Smoke test

```bash
curl -I http://localhost:8000/
# Expected: HTTP/1.1 200 OK  (or 301/302 redirect)
```

If you get a connection refused, the app is still starting. Wait 30 seconds
and try again.

---

## Phase 7 — Nginx + SSL (Production Hardening)

Gunicorn should not be exposed directly to the internet. Nginx handles SSL
termination, compression, and static file serving.

### 7.1 Install Nginx and Certbot

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

### 7.2 Create a DNS A record

In your DNS provider (Route 53, Cloudflare, etc.):

| Type | Name | Value |
|---|---|---|
| A | `portal.yourdomain.com` | `<ELASTIC_IP>` |

Wait for DNS to propagate before continuing (check with `dig portal.yourdomain.com`).

### 7.3 Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/madrona-portal
```

Paste:

```nginx
server {
    listen 80;
    server_name portal.yourdomain.com;

    # Static and media files served directly by Nginx from the Docker volume.
    # The static_data volume is mounted at /vol/web inside the container but
    # is not accessible from the host — gunicorn serves these for now.
    # See note below about a future Nginx-native static setup.

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        client_max_body_size 50M;
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

### 7.4 Obtain an SSL certificate

```bash
sudo certbot --nginx -d portal.yourdomain.com
```

Certbot edits your Nginx config automatically to add SSL and redirect HTTP
to HTTPS. It also installs a cron job to renew the certificate automatically.

### 7.5 Update `ALLOWED_HOSTS`

Add your domain to `.env`:

```ini
ALLOWED_HOSTS=portal.yourdomain.com,<ELASTIC_IP>,localhost
```

Then restart the app container to pick up the change:

```bash
cd ~/portals/madrona-portal
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    up -d --force-recreate app
```

---

## Phase 8 — Keep the Stack Running Across Reboots

Docker Compose does not automatically restart after the EC2 instance reboots.
Set up a systemd service to handle this.

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
    -f docker/docker-compose.yml \
    --env-file .env \
    --profile full \
    up -d
ExecStop=/usr/bin/docker compose \
    -f docker/docker-compose.yml \
    --env-file .env \
    --profile full \
    down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable madrona-portal
```

Test it (optional — simulates a reboot):

```bash
sudo systemctl stop madrona-portal
sudo systemctl start madrona-portal
```

---

## Redeploying After Code Changes

When you push new code and want to redeploy:

**1. On your local machine — commit and push all changes first.**
BuildKit reads from the git object store, so uncommitted changes will not
be included in the image.

**2. On the server — pull and rebuild:**

```bash
cd ~/portals/madrona-portal && git pull
cd ~/portals/madrona-apps/<changed-app> && git pull   # repeat for each changed sub-app

cd ~/portals

docker buildx build \
    --load \
    -f madrona-portal/Dockerfile \
    -t madrona-portal-app:latest \
    .
```

**3. Recreate the app container:**

```bash
cd ~/portals/madrona-portal

docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    up -d --force-recreate app
```

The database and Redis containers are untouched. Downtime is limited to the
container restart (~5–10 seconds).

---

## Useful Commands (on the server)

All `docker compose` commands run from `~/portals/madrona-portal/`.

```bash
# Tail app logs
docker compose -f docker/docker-compose.yml --env-file .env --profile full logs -f app

# Run a Django management command
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py <command>

# Open a Django shell
docker compose -f docker/docker-compose.yml --env-file .env --profile full \
    run --rm app python marco/manage.py shell

# Open a database shell
docker exec -it $(docker compose -f docker/docker-compose.yml --env-file .env ps -q db) \
    psql -U postgres wcoa_docker_db

# Check disk and Docker space usage
df -h
docker system df

# Stop the stack (data preserved)
docker compose -f docker/docker-compose.yml --env-file .env --profile full down

# Full reset — DESTROYS ALL DATA
docker compose -f docker/docker-compose.yml --env-file .env --profile full down -v
```

---

## Services and Ports

| Service | Image | Internal port | Exposed to host |
|---|---|---|---|
| `app` | `madrona-portal-app:latest` | 8000 | Yes — proxied by Nginx |
| `db` | `postgis/postgis:16-3.4` | 5432 | Yes (restrict in security group) |
| `tasks` | `redis:7-alpine` | 6379 | Yes (restrict in security group) |
| `geoportal` | built from `wcoa/docker` | 8080 | Yes (add Nginx location if needed) |
| `elastic` | `elasticsearch:8.19.12` | 9200, 9300 | Yes (restrict in security group) |

> After go-live, update your security group inbound rules to remove public
> access to ports 5432, 6379, 9200, and 9300. These are only needed
> internally between containers on `madronanetwork`.
