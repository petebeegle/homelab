variable "synology" {
  description = "Synology provider connection details supplied from an untracked local tfvars file."
  type = object({
    host       = string
    user       = string
    password   = string
    otp_secret = string
  })
  sensitive = true
}

variable "homelab_user_password" {
  description = "Password for the homelab user (used by Kubernetes CSI driver)"
  type        = string
  sensitive   = true
}
