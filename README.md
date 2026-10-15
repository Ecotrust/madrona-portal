# Madrona Portal

The madrona-portal repository builds a shared base image that contains madrona portal, mp-\*, madrona-\*, and other shared apps.

See a specific portal's documentation for guidance on development and deployment:  

* Mid-Atlantic Ocean Data Portal (MidA)
  * [MidA development setup](https://github.com/Ecotrust/mida-portal/blob/main/docs/DEVELOPMENT_SETUP.md)
  * [MidA production runbook](https://github.com/Ecotrust/mida-portal/blob/main/docs/AWS_DEPLOY_MIDA.md)
* West Coast Ocen Data Portal (WCODP)
  * [WCODP development setup](https://github.com/Ecotrust/wcoa/blob/main/docs/DEVELOPMENT_SETUP.md)
  * [WCODP production runbook](https://github.com/Ecotrust/wcoa/blob/main/docs/AWS_DEPLOY_WCOA.md) 
   
To prepare madrona-portal for deployment on AWS, see [docs/AWS_DEPLOY.md](docs/AWS_DEPLOY.md)

## Docker architecture

The madrona-portal base images are published to GitHub Container Registry (GHCR). Images are built and pushed on merge to `main` using [github actions](.github/workflows/create-and-publish-docker-images.yml). 

The base image is built from this repo's [Dockerfile](docker/Dockerfile) and contains:  

  * image on GHCR `ghcr.io/ecotrust/madrona-portal:{sha,latest}`
  * madrona-\*, mp-\*, and other shared apps 
  * runtime tooling

### Portal overlays

Each portal overlay builds on top of the madrona-portal base image. 

The madrona-portal supports the following portal overlays:  

  - [West Coast Ocean Data Portal (WCODP)](https://github.com/Ecotrust/wcoa)
  - [Mid-Atlantic Data Portal (MidA)](https://github.com/Ecotrust/mida-portal)

Each overlay is built from its own `docker/Dockerfile` and published to GHCR on merge to `main` using github actions.

> *Please note:* The first portal to be Dockerized was `wcoa`. You may come across legacy WCOA-coupled Docker notes.

#### Portal overlay structure

```
┌──────────────────────────────────────────────────────────┐
│  madrona-portal base image                               │       
└──────────────┬─────────────────────────┬─────────────────┘
               │ FROM                    │ FROM
┌──────────────▼─────────────┐ ┌─────────▼─────────────────┐
│  mida-portal overlay image │ │  wcoa overlay image       │
└────────────────────────────┘ └───────────────────────────┘
```

### Portal ownership boundaries

| Concern                                                               | Lives in core (`madrona-portal`) | Lives in project repo (`mida-portal`, `wcoa`) |
| --------------------------------------------------------------------- | -------------------------------- | --------------------------------------------- |
| System deps (GDAL, PostGIS libs, build toolchain)                     | ✔                                |                                               |
| Shared Python deps (`docker-requirements.txt`)                        | ✔                                |                                               |
| Shared mp-\*, madrona-\*  apps                                                      | ✔ (COPY + editable install)      |                                               |
| Entrypoint (connect to db, collectstatic, compress, DB_INIT, server select) | ✔                                |                                               |
| Base compose (db, redis, app skeleton)                                | ✔                                |                                               |
| Project app code + editable install                                   |                                  | ✔                                             |
| Project-only Python deps                                              |                                  | ✔ (`docker/requirements.txt`)                 |
| Project-only services (geoportal, elastic)                            |                                  | ✔ (compose overlay)                           |
| `.env`, ports, DB name, volume names                                  |                                  | ✔                                             |
|  Project settings                                             |                                  | ✔         |

---  

