data "talos_machine_configuration" "this" {
  for_each         = var.nodes
  cluster_name     = var.cluster.name
  cluster_endpoint = "https://${var.cluster.endpoint}:6443"
  talos_version    = var.image.version
  machine_type     = each.value.machine_type
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

data "helm_template" "cilium" {
  name         = "cilium"
  repository   = "https://helm.cilium.io/"
  chart        = "cilium"
  version      = "1.16.6"
  namespace    = "kube-system"
  kube_version = "v1.32.0" # version to use for .Compatibilies.KubeVersion

  values = [
    var.cilium.values
  ]
}

resource "talos_machine_configuration_apply" "this" {
  depends_on = [module.control_planes, module.workers]

  for_each = var.nodes

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.this[each.key].machine_configuration
  node                        = each.key
  config_patches = each.value.machine_type == "controlplane" ? [
    templatefile("${path.module}/templates/control_plane.yaml.tftpl", {
      install_image  = data.talos_image_factory_urls.this.urls.installer
      cilium_install = data.helm_template.cilium.manifest
    })
    ] : [
    templatefile("${path.module}/templates/worker.yaml.tftpl", {
      install_image = data.talos_image_factory_urls.this.urls.installer
    })
  ]
}

resource "talos_machine_secrets" "this" {
  talos_version = var.image.version
}

data "talos_client_configuration" "this" {
  cluster_name         = var.cluster.name
  client_configuration = talos_machine_secrets.this.client_configuration

  nodes     = [for key, value in var.nodes : key]
  endpoints = [for key, value in var.nodes : key if value.machine_type == "controlplane"]
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [talos_machine_configuration_apply.this]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = [for key, value in var.nodes : key if value.machine_type == "controlplane"][0]
  endpoint             = var.cluster.endpoint
}

data "talos_cluster_health" "this" {
  depends_on = [talos_machine_bootstrap.this, talos_machine_configuration_apply.this]

  skip_kubernetes_checks = false
  client_configuration   = data.talos_client_configuration.this.client_configuration
  control_plane_nodes    = [for key, value in var.nodes : key if value.machine_type == "controlplane"]
  worker_nodes           = [for key, value in var.nodes : key if value.machine_type == "worker"]
  endpoints              = data.talos_client_configuration.this.endpoints

  timeouts = {
    read = "10m"
  }
}


resource "talos_cluster_kubeconfig" "this" {
  depends_on           = [talos_machine_bootstrap.this]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = [for key, value in var.nodes : key if value.machine_type == "controlplane"][0]
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
