# The S3 endpoint for Terraform state: Versity S3 Gateway, a Container Manager project on the
# docker share. Objects and their old versions are plain files under /volume2/docker/s3.
# https://s3.petebeegle.com reaches it through a reverse proxy entry set by hand
# (scripts/SYNOLOGY.md). Decision: docs/decisions.md ("Terraform state lives in S3 on the NAS").
#
# Terraform owns the folders, the keys and the .env file the project reads them from. The
# project itself (scripts/synology/s3/docker-compose.yaml) is applied by hand in Container
# Manager, like Nexus: provider 0.6.11's synology_container_project starts a project and then
# fails to decode the build log, dropping it from state, and cannot record an update.

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

# Compose reads ${ROOT_ACCESS_KEY} and ${ROOT_SECRET_KEY} from .env in the project folder, so
# the keys never appear in the project's YAML, which Container Manager shows in its UI.
resource "synology_filestation_file" "s3_env" {
  path      = "/docker/s3/.env"
  overwrite = true
  content   = "ROOT_ACCESS_KEY=${random_password.s3_access_key.result}\nROOT_SECRET_KEY=${random_password.s3_secret_key.result}\n"

  depends_on = [synology_filestation_folder.s3]
}

# Created by #556's apply and imported afterwards; let go of it without stopping the container.
removed {
  from = synology_container_project.s3

  lifecycle {
    destroy = false
  }
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
