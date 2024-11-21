resource "helm_release" "cilium" {
  depends_on = [data.talos_cluster_health.pre_network]
  count      = var.bootstrap_new_cluster ? 1 : 0

  name       = "cilium"
  repository = "https://helm.cilium.io/"
  chart      = "cilium"
  version    = "1.16.1"
  namespace  = "kube-system"

  set {
    name  = "ipam.mode"
    value = "kubernetes"
  }

  set {
    name  = "kubeProxyReplacement"
    value = "true"
  }

  set {
    name  = "securityContext.capabilities.ciliumAgent"
    value = "{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}"
  }

  set {
    name  = "securityContext.capabilities.cleanCiliumState"
    value = "{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}"
  }

  set {
    name  = "cgroup.autoMount.enabled"
    value = "false"
  }

  set {
    name  = "cgroup.hostRoot"
    value = "/sys/fs/cgroup"
  }

  set {
    name  = "k8sServiceHost"
    value = "localhost"
  }

  set {
    name  = "k8sServicePort"
    value = "7445"
  }

  set {
    name  = "hubble.relay.enabled"
    value = "true"
  }

  set {
    name  = "hubble.ui.enabled"
    value = "true"
  }

  set {
    name  = "hostFirewall.enabled"
    value = "true"
  }
}

data "talos_cluster_health" "pre_network" {
  count      = var.bootstrap_new_cluster ? 1 : 0
  depends_on = [talos_machine_bootstrap.this]

  client_configuration   = data.talos_client_configuration.this.client_configuration
  control_plane_nodes    = local.controlplanes_nodes
  worker_nodes           = [for k, v in var.node_data.workers : k]
  endpoints              = data.talos_client_configuration.this.endpoints
  skip_kubernetes_checks = true
}

data "talos_cluster_health" "this" {
  depends_on = [helm_release.cilium]
  count      = var.bootstrap_new_cluster ? 1 : 0

  client_configuration = data.talos_client_configuration.this.client_configuration
  control_plane_nodes  = local.controlplanes_nodes
  worker_nodes         = [for k, v in var.node_data.workers : k]
  endpoints            = data.talos_client_configuration.this.endpoints
}
