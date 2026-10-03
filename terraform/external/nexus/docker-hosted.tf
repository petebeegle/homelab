resource "nexus_blobstore_file" "hosted" {
  name = "docker-hosted"
  path = "/nexus-data/docker-hosted"
}

resource "nexus_repository_docker_hosted" "hosted" {
  name   = "docker-hosted"
  online = true

  docker {
    force_basic_auth = false
    http_port        = 8083
    v1_enabled       = false
  }

  storage {
    blob_store_name                = nexus_blobstore_file.hosted.name
    strict_content_type_validation = true
    write_policy                   = "ALLOW"
  }
}

resource "nexus_security_role" "docker_hosted_publish" {
  roleid      = "docker-hosted-publish"
  name        = "docker-hosted-publish"
  description = "Publish and read hosted Docker images without administration or deletion"
  privileges = [
    "nx-repository-view-docker-docker-hosted-browse",
    "nx-repository-view-docker-docker-hosted-read",
    "nx-repository-view-docker-docker-hosted-add",
    "nx-repository-view-docker-docker-hosted-edit",
  ]
  depends_on = [nexus_repository_docker_hosted.hosted]
}

resource "random_password" "docker_publisher" {
  length           = 32
  special          = true
  override_special = "_%@"
}

resource "nexus_security_user" "docker_publisher" {
  userid    = "docker-publisher"
  firstname = "Docker"
  lastname  = "Publisher"
  password  = random_password.docker_publisher.result
  roles     = [nexus_security_role.docker_hosted_publish.roleid]
  email     = "docker-publisher@example.com"
}

output "nexus_docker_publisher_username" {
  value = nexus_security_user.docker_publisher.userid
}

output "nexus_docker_publisher_password" {
  value     = random_password.docker_publisher.result
  sensitive = true
}

output "nexus_docker_push_endpoint" {
  value = "https://docker-push.lab.petebeegle.com"
}
