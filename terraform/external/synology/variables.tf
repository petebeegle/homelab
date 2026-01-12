variable "homelab_user_password" {
  description = "Password for the homelab user (used by Kubernetes CSI driver)"
  type        = string
  sensitive   = true
}
