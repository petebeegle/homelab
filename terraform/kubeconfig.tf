resource "talos_cluster_kubeconfig" "this" {
  depends_on           = [talos_machine_bootstrap.this]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = local.controlplanes_nodes[0]

  provisioner "local-exec" {
    command = <<EOT
      mkdir -p ~/.kube
      echo '${talos_cluster_kubeconfig.this.kubeconfig_raw}' > ~/.kube/config
      chmod 600 ~/.kube/config
    EOT

  }
}

output "kubeconfig" {
  value     = talos_cluster_kubeconfig.this.kubeconfig_raw
  sensitive = true
}
