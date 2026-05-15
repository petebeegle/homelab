# Source this file from Bash or Zsh to add opt-in kubectl and Flux shortcuts.
#
# These helpers set KUBECONFIG only for the command process they start.

kd() {
  KUBECONFIG="${HOME}/.kube/homelab-development.config" kubectl "$@"
}

kp() {
  KUBECONFIG="${HOME}/.kube/homelab-production.config" kubectl "$@"
}

fd() {
  KUBECONFIG="${HOME}/.kube/homelab-development.config" flux "$@"
}

fp() {
  KUBECONFIG="${HOME}/.kube/homelab-production.config" flux "$@"
}
