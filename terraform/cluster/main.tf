module "talos" {
  source = "./modules/talos"

  providers = {
    proxmox = proxmox
    talos   = talos
    helm    = helm
  }

  cluster = {
    name     = "proxmox-k8s-cluster"
    endpoint = "192.168.30.150"
  }

  image = {
    version = "v1.11.2"
  }

  cilium = {
    values = file("${path.module}/../../kubernetes/infra/network/cilium/values.yaml")
  }

  nodes = var.nodes

  docker_image_proxy = {
    enabled = true
    registry = {
      user     = var.docker_user
      password = var.docker_password
    }
  }

  nfs_server = {
    name             = "remote-nas"
    destination_path = "/mnt/pve/remote-nas/template/iso"
    host             = var.nfs_host
    user             = var.nfs_user
  }
}

resource "null_resource" "bootstrap_script" {
  depends_on = [module.talos]

  provisioner "local-exec" {
    environment = {
      GITHUB_TOKEN = var.github_token
      GITHUB_USER  = var.github_user
    }

    command = file("${path.module}/scripts/flux-install.sh")
  }
}

output "kubeconfig" {
  value     = module.talos.kubeconfig
  sensitive = true
}

output "talosconfig" {
  value     = module.talos.talosconfig
  sensitive = true
}
