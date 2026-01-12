output "user_exists" {
  description = "Whether the user already existed"
  value       = data.external.check_user.result.exists == "true"
}

output "username" {
  description = "The username"
  value       = var.username
}

output "user_created" {
  description = "Whether the user was created by Terraform"
  value       = length(synology_api.user) > 0
}
