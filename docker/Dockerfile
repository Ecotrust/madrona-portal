# =============================================================================
# Madrona Portal — Production Dockerfile
# Base: python:3.12-slim | Django 4.2+ | Wagtail 7.0+ 
# =============================================================================
FROM python:3.12-slim

# Prevent apt from blocking on interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Python & app environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/local/apps/madrona-portal

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    libpq-dev \
    gdal-bin libgdal-dev \
    libgeos-dev \
    libjpeg-dev zlib1g-dev libtool \
    libprotobuf-c-dev libjson-c-dev \
    perl libxml2-dev \
    libproj-dev proj-bin \
    libffi-dev openssl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Copy only dependency inputs to leverage Docker layer caching
# ---------------------------------------------------------------------------
COPY madrona-portal/docker/docker-requirements.txt /requirements.txt

COPY madrona-apps/mp-layers ./apps/mp-layers

# ---------------------------------------------------------------------------
# Python dependencies
# - Cache pip downloads/wheels
# - Install the package needed for local resolution before requirements
# - Keep GDAL in its own layer so it can cache independently
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-deps -e ./apps/mp-layers && \
    pip install -r /requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "GDAL==$(gdal-config --version)"

# ---------------------------------------------------------------------------
# Copy application source
# ---------------------------------------------------------------------------
COPY madrona-portal/marco          ./marco
COPY madrona-portal/apps/__init__.py ./apps/__init__.py
COPY madrona-portal/assets         ./assets
COPY madrona-portal/bower_components ./bower_components
COPY madrona-portal/docker/entrypoint.sh /entrypoint.sh
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
COPY madrona-apps/mp-map-groups          ./apps/mp-map-groups
COPY madrona-apps/mp-proxy               ./apps/mp-proxy
COPY madrona-apps/mp-survey              ./apps/mp-survey
COPY madrona-apps/mp-visualize           ./apps/mp-visualize
COPY madrona-apps/p97-nursery            ./apps/p97-nursery

# ---------------------------------------------------------------------------# Install local sub-apps as editable (must run after all COPY commands)
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    -e ./apps/mp-data-manager \
    -e ./apps/django_url_shortener/url_short \
    -e ./apps/madrona-analysistools \
    -e ./apps/mp-visualize \
    -e ./apps/madrona-features \
    -e ./apps/mp-accounts \
    -e ./apps/madrona-scenarios \
    -e ./apps/madrona-manipulators \
    -e ./apps/mp-drawing \
    -e ./apps/mp-explore \
    -e ./apps/mp-map-groups \
    -e ./apps/p97-nursery \
    -e ./apps/mp-proxy \
    -e ./apps/mp-survey

# ---------------------------------------------------------------------------# Runtime setup
# ---------------------------------------------------------------------------
RUN chmod 755 /entrypoint.sh && \
    mkdir -p /vol/web/static && \
    useradd --create-home --shell /bin/sh madrona_user && \
    chown -R madrona_user:madrona_user /vol /usr/local/apps/madrona-portal && \
    chmod -R 775 /vol/web

EXPOSE 8000
EXPOSE 8008

CMD ["/entrypoint.sh"]
