
locals {
  cluster_name        = "proxmox-k8s-cluster"
  cluster_endpoint    = "https://${local.controlplanes_nodes[0]}:6443"
  controlplanes_nodes = [for k, v in var.node_data.controlplanes : k]

  node_gateway = "192.168.3.1"
}

module "talos_iso" {
  source = "./modules/talos"

  talos_version = "v1.8.3"

  destination_user = var.nas_user
  destination_host = var.nas_ip
  destination_port = var.nas_port
}

resource "talos_machine_secrets" "this" {}
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

  provisioner "local-exec" {
    command = templatefile("${path.module}/scripts/kubeconfig-install.sh", {
      kubeconfig = talos_cluster_kubeconfig.this.kubeconfig_raw
    })
  }
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

resource "null_resource" "talos_config" {
  depends_on = [data.talos_client_configuration.this]

  provisioner "local-exec" {
    command = templatefile("${path.module}/scripts/talosconfig-install.sh", {
      talosconfig = data.talos_client_configuration.this.talos_config
    })
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
