# The S3 endpoint for Terraform state: Versity S3 Gateway as a Container Manager project on
# the docker share. Objects and their old versions are plain files under /volume2/docker/s3.
# https://s3.petebeegle.com reaches it through a reverse proxy entry set by hand
# (scripts/SYNOLOGY.md). Decision: docs/decisions.md ("Terraform state lives in S3 on the NAS").

resource "synology_filestation_folder" "s3" {
  for_each = toset(["data", "versions"])

  path           = "/docker/s3/${each.key}"
  create_parents = true
}

resource "random_password" "s3_access_key" {
  length  = 20
  special = false
  upper   = true
  lower   = false
}

resource "random_password" "s3_secret_key" {
  length  = 40
  special = false
}

resource "synology_filestation_file" "s3_env" {
  path      = "/docker/s3/.env"
  overwrite = true
  content   = "ROOT_ACCESS_KEY=${random_password.s3_access_key.result}\nROOT_SECRET_KEY=${random_password.s3_secret_key.result}\n"

  depends_on = [synology_filestation_folder.s3]
}

# The compose file stays the source (Renovate tracks its image), but the project is described
# through `services`: provider 0.6.11 replaces a literal `content` with one built from `services`
# and fails the plan.
locals {
  s3_service = yamldecode(file("${path.module}/../../../scripts/synology/s3/docker-compose.yaml")).services.versitygw
}

resource "synology_container_project" "s3" {
  name       = "s3"
  share_path = "/docker/s3"
  run        = true

  services = {
    versitygw = {
      image          = local.s3_service.image
      container_name = local.s3_service.container_name
      restart        = local.s3_service.restart
      command        = local.s3_service.command
      # Compose fills these from .env in the project folder (synology_filestation_file.s3_env).
      # The keys must not appear here: the provider computes the project's `content` from
      # `services` without a sensitive mark, so every plan would print them.
      environment = {
        ROOT_ACCESS_KEY = "$${ROOT_ACCESS_KEY}"
        ROOT_SECRET_KEY = "$${ROOT_SECRET_KEY}"
      }
      ports = [for port in local.s3_service.ports : {
        host_ip   = split(":", port)[0]
        published = split(":", port)[1]
        target    = tonumber(split(":", port)[2])
      }]
      volumes = [for volume in local.s3_service.volumes : {
        type   = "bind"
        source = split(":", volume)[0]
        target = split(":", volume)[1]
      }]
    }
  }

  depends_on = [synology_filestation_folder.s3, synology_filestation_file.s3_env]
}

output "s3_access_key" {
  description = "Access key for the S3 gateway; store it in 1Password (scripts/SYNOLOGY.md)."
  value       = random_password.s3_access_key.result
  sensitive   = true
}

output "s3_secret_key" {
  description = "Secret key for the S3 gateway; store it in 1Password (scripts/SYNOLOGY.md)."
  value       = random_password.s3_secret_key.result
  sensitive   = true
}
