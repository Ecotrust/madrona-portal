# Madrona Portal

The madrona-portal repository builds a base image that contains madrona-portal, mp-\*, madrona-\*, and other shared apps.

To prepare madrona-portal for deployment on AWS, see [docs/AWS_DEPLOY.md](docs/AWS_DEPLOY.md)

## Docker architecture

The madrona-portal base images are published to GitHub Container Registry (GHCR). Images are built and pushed on merge to `main` using [github actions](.github/workflows/create-and-publish-docker-images.yml). 

### Portal application images

Each portal app image builds on top of the madrona-portal base image. 

The madrona-portal supports the following portal app images:  

  - [West Coast Ocean Data Portal (WCODP)](https://github.com/Ecotrust/wcoa)
  - [Mid-Atlantic Data Portal (MidA)](https://github.com/Ecotrust/mida-portal)

Each portal app image is built from its own `docker/Dockerfile` and published to GHCR on merge to `main` using github actions.

See a specific portal app's documentation for guidance on development and deployment:  

* Mid-Atlantic Ocean Data Portal (MidA)
  * [MidA development setup](https://github.com/Ecotrust/mida-portal/blob/main/docs/DEVELOPMENT_SETUP.md)
  * [MidA production runbook](https://github.com/Ecotrust/mida-portal/blob/main/docs/AWS_DEPLOY_MIDA.md)
* West Coast Ocen Data Portal (WCODP)
  * [WCODP development setup](https://github.com/Ecotrust/wcoa/blob/main/docs/DEVELOPMENT_SETUP.md)
  * [WCODP production runbook](https://github.com/Ecotrust/wcoa/blob/main/docs/AWS_DEPLOY_WCOA.md) 

> *Please note:* The first portal app image to be Dockerized was `wcoa`. You may come across legacy WCOA-coupled Docker notes.

#### Portal app image structure

```
┌──────────────────────────────────────────────────────────┐
│  madrona-portal base image                               │       
└──────────────┬─────────────────────────┬─────────────────┘
               │ FROM                    │ FROM
┌──────────────▼─────────────┐ ┌─────────▼─────────────────┐
│  mida-portal app image     │ │  wcoa app image           │
└────────────────────────────┘ └───────────────────────────┘
```

### Portal ownership boundaries

| Concern                                                               | Lives in core (`madrona-portal`) | Lives in project repo (`mida-portal`, `wcoa`) |
| --------------------------------------------------------------------- | -------------------------------- | --------------------------------------------- |
| System deps (GDAL, PostGIS libs, build toolchain)                     | ✔                                |                                               |
| Shared Python deps (`docker-requirements.txt`)                        | ✔                                |                                               |
| Shared mp-\*, madrona-\*  apps                                        | ✔ (COPY + editable install)      |                                               |
| Entrypoint (db connect, collectstatic, compress, DB_INIT, server)     | ✔                                |                                               |
| Base compose (db, redis, app skeleton)                                | ✔                                |                                               |
| Project app code + editable install                                   |                                  | ✔                                             |
| Project-only Python deps                                              |                                  | ✔ (`docker/requirements.txt`)                 |
| Project-only services (Geoportal, Elasticsearch)                      |                                  | ✔ (compose overlay)                           |
| `.env`, ports, DB name, volume names                                  |                                  | ✔                                             |
|  Project settings                                                     |                                  | ✔                                             |

---  

