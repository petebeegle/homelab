# Configure Nexus

- [Prerequisites](#prerequisites)
- [Run Nexus](#run-nexus)
- [Configure A Docker Registry](#configure-a-docker-registry)
    - [Set up a docker user](#set-up-a-docker-user)
    - [Create a Proxy Registry](#create-a-proxy-registry)
    - [Test the Proxy Registry](#test-the-proxy-registry)

## Prerequisites
- Run [Configure Synology](./SYNOLOGY.md), configuring a `nexus` and `docker-registry` certificate and reverse proxy
- SSH is enabled (temporarily)

## Run Nexus
1. Install `Container Manager` via `Package Center`
2. Ensure the folder `/volume2/docker/nexus` exists 
3. Open `Container Manager` and create a new project
4. Upload [nexus.docker-compose.yaml](./synology/nexus.docker-compose.yaml)
5. Start the project. This will run the docker-compose exposing nexus on ports `8081` and `8082`.

> [!IMPORTANT]
> There may be some discrepancies in configurations, particularly the user id (`1027`) and the volume mount location `/volume2`.

> [!NOTE]
> Get the initial admin password from `/docker/nexus/nexus-data/admin.password`

## Configure A Docker Registry

### Set up a docker user
1. Create a new role named `docker-group-view` with the following `Applied Privileges`:
    - `nx-repository-view-docker-docker-group-*`
2. Create a new user named `docker` with `docker-group-view` granted

### Create a Proxy Registry
1. Create a `Blob Store` of type `File` called `docker-hub` at path `docker-hub`
2. Create a new repository for `docker (proxy)` with the following settings:

| Setting                | Value                          |
|------------------------|--------------------------------|
| Name                   | docker-proxy                   |
| Type                   | docker (proxy)                 |
| Remote Storage         | https://registry-1.docker.io   |
| Docker Index           | Use Docker Hub                 |
| Auto blocking enabled  | `true`                         |
| Blob store             | docker-hub                     |

3. Create a new repository `docker (group)` with the following settings:

| Setting                | Value                          |
|------------------------|--------------------------------|
| Name                   | docker-group                   |
| Type                   | docker (group)                 |
| HTTP                   | `8082`                         |
| Enable Docker V1 API   | `true`                         |
| Group Members          | docker-proxy                   |


### Test the Proxy Registry
```sh
docker login docker-registry.example.com
docker pull docker-registry.example.com/nginx:latest
```
