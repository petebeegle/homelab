variable "github_token" {
  description = "GitHub token to use for the bootstrap script"
  type        = string
  sensitive   = true
}

variable "github_user" {
  description = "GitHub user to use for the bootstrap script"
  type        = string
}

variable "docker_user" {
    description = "Docker user for authenticating to the pass-through docker registry"
    type        = string
}

variable "docker_password" {
    description = "Docker password for authenticating to the pass-through docker registry"
    type        = string
    sensitive   = true
}
