resource "nexus_security_role" "docker_group_view" {
  roleid      = "docker-group-view"
  name        = "docker-group-view"
  description = "Grants read access to the docker group repository"
  privileges = [
    "nx-repository-view-docker-docker-group-*"
  ]

  depends_on = [nexus_repository_docker_group.group]
}

resource "random_password" "docker_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

resource "nexus_security_realms" "docker" {
  active = [
    "NexusAuthenticatingRealm",
    "DockerToken"
  ]
}

resource "nexus_security_user" "docker" {
  userid    = "docker"
  firstname = "Docker"
  lastname  = "User"
  password  = random_password.docker_password.result
  roles     = ["docker-group-view"]
  email     = "docker@example.com"
}

resource "nexus_blobstore_file" "file" {
  name = "docker-hub"
  path = "/nexus-data/docker-hub"

  soft_quota {
    limit = 1024000000
    type  = "spaceRemainingQuota"
  }
}

resource "nexus_repository_docker_proxy" "proxy" {
  name   = "docker-proxy"
  online = true

  docker {
    force_basic_auth = false
    v1_enabled       = false
  }

  docker_proxy {
    index_type = "HUB"
  }

  storage {
    blob_store_name                = "docker-hub"
    strict_content_type_validation = true
  }

  proxy {
    remote_url       = "https://registry-1.docker.io"
    content_max_age  = 1440
    metadata_max_age = 1440
  }

  negative_cache {
    enabled = true
    ttl     = 1440
  }

  http_client {
    blocked    = false
    auto_block = true
  }

  depends_on = [nexus_blobstore_file.file]
}

resource "nexus_repository_docker_group" "group" {
  name   = "docker-group"
  online = true

  docker {
    force_basic_auth = false
    http_port        = 8082
    https_port       = 8433
    v1_enabled       = true
  }

  group {
    member_names = [
      nexus_repository_docker_proxy.proxy.name
    ]
  }

  storage {
    blob_store_name                = "docker-hub"
    strict_content_type_validation = true
  }
}

output "nexus_docker_password" {
  value     = random_password.docker_password.result
  sensitive = true
}
