data "github_repository" "this" {
  full_name = var.github_slug
}

resource "flux_bootstrap_git" "this" {
  depends_on = [data.github_repository.this, data.talos_cluster_health.this]

  embedded_manifests = true
  path               = "kubernetes/cluster"
}
