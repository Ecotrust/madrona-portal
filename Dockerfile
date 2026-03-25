# pull official base image — Ubuntu 24.04 LTS (Noble Numbat)
FROM ubuntu:24.04

# prevent apt from blocking on interactive questions during build
ENV DEBIAN_FRONTEND=noninteractive

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MP_PROJECT_CONFIG=config.wcoa.docker.ini

# set work directory
WORKDIR /usr/local/apps/madrona-portal

# copy project
COPY madrona_portal/marco /usr/local/apps/madrona-portal/marco
COPY madrona_portal/apps/__init__.py /usr/local/apps/madrona-portal/apps/__init__.py
COPY madrona_portal/assets /usr/local/apps/madrona-portal/assets
COPY madrona_portal/bower_components /usr/local/apps/madrona-portal/bower_components
COPY madrona_portal/docker/entrypoint.sh /entrypoint.sh
COPY madrona_portal/docker/docker-requirements.txt /requirements.txt
COPY madrona_portal/backups /usr/local/apps/madrona-portal/backups

COPY madrona-apps/django_url_shortener /usr/local/apps/madrona-portal/apps/django_url_shortener
COPY madrona-apps/madrona-analysistools /usr/local/apps/madrona-portal/apps/madrona-analysistools
COPY madrona-apps/madrona-features /usr/local/apps/madrona-portal/apps/madrona-features
COPY madrona-apps/madrona-manipulators /usr/local/apps/madrona-portal/apps/madrona-manipulators
COPY madrona-apps/madrona-scenarios /usr/local/apps/madrona-portal/apps/madrona-scenarios
COPY madrona-apps/mp-accounts /usr/local/apps/madrona-portal/apps/mp-accounts
COPY madrona-apps/mp-data-manager /usr/local/apps/madrona-portal/apps/mp-data-manager
COPY madrona-apps/mp-drawing /usr/local/apps/madrona-portal/apps/mp-drawing
COPY madrona-apps/mp-explore /usr/local/apps/madrona-portal/apps/mp-explore
COPY madrona-apps/mp-layers /usr/local/apps/madrona-portal/apps/mp-layers
COPY madrona-apps/mp-map-groups /usr/local/apps/madrona-portal/apps/mp-map-groups
COPY madrona-apps/mp-proxy /usr/local/apps/madrona-portal/apps/mp-proxy
COPY madrona-apps/mp-visualize /usr/local/apps/madrona-portal/apps/mp-visualize
COPY madrona-apps/p97-nursery /usr/local/apps/madrona-portal/apps/p97-nursery
COPY madrona-apps/wcoa /usr/local/apps/madrona-portal/apps/wcoa

# install system dependencies — mirrors the Ubuntu 24.04 wiki install
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
      postgresql postgresql-contrib postgresql-client postgis \
      postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment so pip installs don't conflict with system Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the local layers app first so later package resolution can satisfy
# any dependency on the mp-layers distribution from the local checkout.
RUN pip install --upgrade pip setuptools wheel && \
  pip install --no-deps -e /usr/local/apps/madrona-portal/apps/mp-layers && \
  pip install -r /requirements.txt

# Install GDAL Python bindings matched to the system GDAL version.
# Installed separately so this layer is cached independently.
RUN pip install "GDAL==$(gdal-config --version)" --no-cache-dir

RUN chmod +x /entrypoint.sh

RUN mkdir -p /vol/web/media /vol/web/static

RUN useradd --create-home --shell /bin/sh madrona_user
RUN chown -R madrona_user:madrona_user /vol
RUN chown -R madrona_user:madrona_user /usr/local/apps/madrona-portal
RUN chmod -R 755 /vol/web

USER madrona_user

EXPOSE 8000

CMD ["/entrypoint.sh"]
