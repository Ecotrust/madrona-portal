# pull official base image
FROM python:3.9.6-alpine
#FROM alpine:3.14
#FROM python:3.8.10-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/local/apps/madrona-portal

# copy project
COPY ./marco /usr/local/apps/madrona-portal/marco
COPY ./apps /usr/local/apps/madrona-portal/apps
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./marco/docker-requirements.txt ./marco/requirements.txt

# install dependencies
RUN \
    apk update &&\
    apk add --no-cache --virtual .build-deps \
      python3-dev autoconf automake make protobuf-c-dev json-c-dev perl libxml2-dev \
      proj proj-dev proj-util musl-dev gcc binutils \
      g++ jpeg-dev libjpeg zlib-dev gdal gdal-tools geos-dev libtool \
      postgresql-dev postgresql-libs \
      libffi-dev \
      pkgconfig openssl &&\
    apk add --no-cache --update \
      libpq gdal-dev && \
    pip install --upgrade pip &&\
    pip install -r /usr/local/apps/madrona-portal/marco/requirements.txt &&\
    apk --purge del .build-deps

RUN chmod +x /entrypoint.sh

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D madrona_user
RUN chown -R madrona_user:madrona_user /vol
RUN chmod -R 755 /vol/web

USER madrona_user

CMD ["/entrypoint.sh"]
