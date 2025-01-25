module "talos" {
  source = "./modules/talos"

  providers = {
    proxmox = proxmox
    talos   = talos
    helm    = helm
  }

  cluster = {
    name     = "proxmox-k8s-cluster"
    endpoint = "192.168.3.60"
  }

  image = {
    version = "v1.9.1"
  }

  ssh = {
    user = "vscode"
    host = "192.168.3.2"
  }

  cilium = {
    values = file("${path.module}/../kubernetes/infra/cilium/values.yaml")
  }

  nodes = {
    "192.168.3.60" = {
      node         = "pve01"
      vm_id        = 102
      memory       = 8192
      cores        = 2
      machine_type = "controlplane"
    },
    "192.168.3.63" = {
      node         = "pve02"
      vm_id        = 201
      memory       = 8192
      cores        = 2
      machine_type = "controlplane"

    },
    "192.168.3.64" = {
      node         = "pve03"
      vm_id        = 300
      memory       = 8192
      cores        = 2
      machine_type = "controlplane"
    },
    "192.168.3.61" = {
      node         = "pve01"
      vm_id        = 103
      memory       = 16384
      cores        = 2
      machine_type = "worker"
    },
    "192.168.3.62" = {
      node         = "pve02"
      vm_id        = 200
      memory       = 16384
      cores        = 2
      machine_type = "worker"

    },
    "192.168.3.65" = {
      node         = "pve03"
      vm_id        = 301
      memory       = 16384
      cores        = 2
      machine_type = "worker"

    }
    "192.168.3.66" = {
      node         = "pve04"
      vm_id        = 400
      memory       = 63488
      cores        = 28
      machine_type = "worker"

    }
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
