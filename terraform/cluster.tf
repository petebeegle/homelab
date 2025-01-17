
locals {
  cluster_name        = "proxmox-k8s-cluster"
  cluster_endpoint    = "https://${local.controlplanes_nodes[0]}:6443"
  controlplanes_nodes = [for k, v in var.node_data.controlplanes : k]

  node_gateway = "192.168.3.1"
  install_patch = {
    machine = {
        install = {
            image = module.talos_iso.install_image
        }
    }
  }
}

module "talos_iso" {
  source = "./modules/talos"

  talos_version = var.talosos_version

  destination_host = var.destination_host
  destination_user = var.destination_user

  extensions = [
    "btrfs",
    "iscsi-tools",
  ]
}

resource "talos_machine_secrets" "this" {
  talos_version = var.talosos_version
}

data "talos_client_configuration" "this" {
  cluster_name         = local.cluster_name
  client_configuration = talos_machine_secrets.this.client_configuration
  endpoints            = local.controlplanes_nodes
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [talos_machine_configuration_apply.controlplane]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = local.controlplanes_nodes[0]
}

data "talos_cluster_health" "this" {
  depends_on = [talos_machine_bootstrap.this, talos_machine_configuration_apply.controlplane, talos_machine_configuration_apply.worker]

  client_configuration = data.talos_client_configuration.this.client_configuration
  control_plane_nodes  = local.controlplanes_nodes
  worker_nodes         = [for k, v in var.node_data.workers : k]
  endpoints            = data.talos_client_configuration.this.endpoints
}

resource "talos_cluster_kubeconfig" "this" {
  depends_on           = [talos_machine_bootstrap.this]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = local.controlplanes_nodes[0]
}

resource "null_resource" "bootstrap_script" {
  depends_on = [data.talos_cluster_health.this, talos_cluster_kubeconfig.this, talos_machine_bootstrap.this, talos_machine_configuration_apply.controlplane, talos_machine_configuration_apply.worker]

  provisioner "local-exec" {
    environment = {
      GITHUB_TOKEN = var.github_token
      GITHUB_USER  = var.github_user
    }

    command = file("${path.module}/scripts/flux-install.sh")
  }
}

resource "null_resource" "kube_config" {
  depends_on = [talos_cluster_kubeconfig.this]

  provisioner "local-exec" {
    command = templatefile("${path.module}/scripts/kubeconfig-install.sh", {
      kubeconfig = talos_cluster_kubeconfig.this.kubeconfig_raw
    })
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "null_resource" "talos_config" {
  depends_on = [data.talos_client_configuration.this]

  provisioner "local-exec" {
    command = templatefile("${path.module}/scripts/talosconfig-install.sh", {
      talosconfig = data.talos_client_configuration.this.talos_config
    })
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

output "kubeconfig" {
  value     = talos_cluster_kubeconfig.this.kubeconfig_raw
  sensitive = true
}


output "talosconfig" {
  value     = data.talos_client_configuration.this.talos_config
  sensitive = true
}
