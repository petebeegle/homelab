# Source this file from Bash or Zsh to add opt-in kubectl shortcuts.
#
# These helpers set KUBECONFIG only for the kubectl process they start.

kd() {
  KUBECONFIG="${HOME}/.kube/homelab-development.config" kubectl "$@"
}

kp() {
  KUBECONFIG="${HOME}/.kube/homelab-production.config" kubectl "$@"
}
