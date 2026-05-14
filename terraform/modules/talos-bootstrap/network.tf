data "helm_template" "cilium" {
  name         = "cilium"
  repository   = "https://helm.cilium.io/"
  chart        = "cilium"
  version      = "1.19.3"
  namespace    = "kube-system"
  kube_version = "v1.35.0" # version to use for .Compatibilies.KubeVersion

  values = [
    file("${path.root}/../../kubernetes/infra/network/cilium/values.yaml")
  ]
}
