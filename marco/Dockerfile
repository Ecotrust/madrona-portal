# pull official base image
#FROM python:3.9.6-alpine
FROM python:3.8.10-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ../docker/requirements.txt .

# install dependencies
RUN \
    apk update &&\
    apk add --no-cache --virtual .build-deps \
      python3-dev musl-dev gcc \
      binutils \
      postgresql-dev postgresql-libs \
      libffi-dev \
      pkgconfig openssl &&\
    apk add --no-cache --update \
      libpq gdal-dev && \
    pip install --upgrade pip &&\
    pip install -r requirements.txt &&\
    apk --purge del .build-deps

# copy project
COPY ./ /usr/local/apps/madrona_portal/marco
COPY ../docker/entrypoint.sh /entrypoint.sh

# set work directory
WORKDIR /usr/local/apps/madrona_portal/marco

RUN chmod +x /entrypoint.sh

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D madrona_user
RUN chown -R madrona_user:madrona_user /vol
RUN chmod -R 755 /vol/web

USER madrona_user

CMD ["/entrypoint.sh"]
