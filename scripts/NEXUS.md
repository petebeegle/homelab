# Configure Nexus

- [Prerequisites](#prerequisites)
- [Run Nexus](#run-nexus)
- [Configure A Docker Registry](#configure-a-docker-registry)
    - [Set up a docker user](#set-up-a-docker-user)
    - [Create a Proxy Registry](#create-a-proxy-registry)
    - [Test the Proxy Registry](#test-the-proxy-registry)

## Prerequisites
- Run [Configure Synology](./SYNOLOGY.md), configuring a `nexus` and `docker-registry` certificate and reverse proxy

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

Run the environment terraform to provision the docker registry:
```shell
cd /workspaces/homelab/terraform/external
terraform apply -auto
```

### Test the Proxy Registry
```sh
docker login docker-registry.example.com
docker pull docker-registry.example.com/nginx:latest
```
