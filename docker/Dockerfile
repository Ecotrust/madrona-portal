# =============================================================================
# Madrona Portal — Production Dockerfile
# Base: Ubuntu 24.04 LTS | Django 4.2+ | Wagtail 7.0+ | Python 3.10+
# =============================================================================
FROM ubuntu:24.04

# Prevent apt from blocking on interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Python & app environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    MP_PROJECT_CONFIG=config.wcoa.docker.ini

WORKDIR /usr/local/apps/madrona-portal

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip python3-dev python3-venv \
      python-is-python3 \
      build-essential pkg-config \
      libpq-dev \
      gdal-bin libgdal-dev \
      libgeos-dev \
      libjpeg-dev zlib1g-dev libtool \
      libprotobuf-c-dev libjson-c-dev \
      perl libxml2-dev \
      libproj-dev proj-bin \
      libffi-dev openssl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python virtual environment
# ---------------------------------------------------------------------------
RUN python3 -m venv /opt/venv

# ---------------------------------------------------------------------------
# Copy application source
# ---------------------------------------------------------------------------
COPY madrona-portal/marco          ./marco
COPY madrona-portal/apps/__init__.py ./apps/__init__.py
COPY madrona-portal/assets         ./assets
COPY madrona-portal/bower_components ./bower_components
COPY madrona-portal/docker/entrypoint.sh /entrypoint.sh
COPY madrona-portal/docker/docker-requirements.txt /requirements.txt
COPY madrona-portal/backups        ./backups

COPY madrona-apps/django_url_shortener   ./apps/django_url_shortener
COPY madrona-apps/madrona-analysistools  ./apps/madrona-analysistools
COPY madrona-apps/madrona-features       ./apps/madrona-features
COPY madrona-apps/madrona-manipulators   ./apps/madrona-manipulators
COPY madrona-apps/madrona-scenarios      ./apps/madrona-scenarios
COPY madrona-apps/mp-accounts            ./apps/mp-accounts
COPY madrona-apps/mp-data-manager        ./apps/mp-data-manager
COPY madrona-apps/mp-drawing             ./apps/mp-drawing
COPY madrona-apps/mp-explore             ./apps/mp-explore
COPY madrona-apps/mp-layers              ./apps/mp-layers
COPY madrona-apps/mp-map-groups          ./apps/mp-map-groups
COPY madrona-apps/mp-proxy               ./apps/mp-proxy
COPY madrona-apps/mp-survey              ./apps/mp-survey
COPY madrona-apps/mp-visualize           ./apps/mp-visualize
COPY madrona-apps/p97-nursery            ./apps/p97-nursery
COPY madrona-apps/wcoa                   ./apps/wcoa

# ---------------------------------------------------------------------------
# Python dependencies
# Install mp-layers first (no-deps) so later resolution can satisfy any
# local dependency on its distribution before installing the rest.
# ---------------------------------------------------------------------------
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-deps -e ./apps/mp-layers && \
    pip install -r /requirements.txt

# GDAL Python bindings — installed in a separate layer to preserve Docker
# cache when the rest of requirements.txt changes.
RUN pip install "GDAL==$(gdal-config --version)" --no-cache-dir

# ---------------------------------------------------------------------------
# Runtime setup
# ---------------------------------------------------------------------------
RUN chmod 755 /entrypoint.sh && \
    mkdir -p /vol/web/media /vol/web/static && \
    useradd --create-home --shell /bin/sh madrona_user && \
    chown -R madrona_user:madrona_user /vol /usr/local/apps/madrona-portal && \
    chmod -R 755 /vol/web

USER madrona_user

EXPOSE 8000
EXPOSE 8008

CMD ["/entrypoint.sh"]
