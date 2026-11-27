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

resource "synology_container_project" "s3" {
  name       = "s3"
  share_path = "/docker/s3"
  run        = true
  content = templatefile("${path.module}/../../../scripts/synology/s3/docker-compose.yaml", {
    access_key = random_password.s3_access_key.result
    secret_key = random_password.s3_secret_key.result
  })

  depends_on = [synology_filestation_folder.s3]
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
