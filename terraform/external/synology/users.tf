module "homelab_user" {
  source = "./modules/synology-user"

  synology_host = "https://192.168.30.99:5001"
  username      = "homelab"
  password      = var.homelab_user_password
  description   = "User for Kubernetes CSI driver"
  groups        = ["administrators"]
}
