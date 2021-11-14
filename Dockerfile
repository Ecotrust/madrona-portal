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
COPY ./assets /usr/local/apps/madrona-portal/assets
COPY ./bower_components /usr/local/apps/madrona-portal/bower_components
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./docker/docker-requirements.txt /requirements.txt

# install dependencies
RUN \
    apk update &&\
    apk add --no-cache --virtual .build-deps \
      autoconf automake make \
      musl-dev gcc binutils g++ \
      libffi-dev \
      pkgconfig openssl \
      &&\
    apk add --no-cache --update \
      python3-dev \
      postgresql-dev postgresql-libs \
      jpeg-dev libjpeg zlib-dev libtool \
      libpq gdal gdal-tools geos-dev gdal-dev \
      protobuf-c-dev json-c-dev perl libxml2-dev \
      proj proj-dev proj-util \
      && \
    pip install --upgrade pip &&\
    pip install -r /requirements.txt
    #&&\
    #apk --purge del .build-deps

RUN chmod +x /entrypoint.sh

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D madrona_user
RUN chown -R madrona_user:madrona_user /vol
RUN chown -R madrona_user:madrona_user /usr/local/apps/madrona-portal
RUN chmod -R 755 /vol/web

USER madrona_user

CMD ["/entrypoint.sh"]
