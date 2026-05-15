data "helm_template" "cilium" {
  name         = "cilium"
  repository   = "https://helm.cilium.io/"
  chart        = "cilium"
  version      = "1.19.3"
  namespace    = "kube-system"
  kube_version = var.kubernetes_version # version to use for .Compatibilies.KubeVersion

  values = [
    templatefile("${path.root}/../../kubernetes/infra/network/cilium/values.yaml", {
      cilium_operator_replicas = var.cilium_operator_replicas
    }),
    file("${path.module}/templates/cilium-bootstrap-values.yaml")
  ]
}
