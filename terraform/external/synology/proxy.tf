resource "synology_api" "docker_registry_reverse_proxy" {
  api     = "SYNO.Core.AppPortal.ReverseProxy"
  method  = "create"
  version = 1

  parameters = {
    entry = jsonencode({
      description            = "Docker Registry"
      proxy_connect_timeout  = 60
      proxy_read_timeout     = 60
      proxy_send_timeout     = 60
      proxy_http_version     = 1
      proxy_intercept_errors = false

      frontend = {
        acl      = null
        fqdn     = "docker-registry.petebeegle.com"
        port     = 443
        protocol = 1 # HTTPS
        https = {
          hsts = false
        }
      }

      backend = {
        fqdn     = "localhost"
        port     = 8082
        protocol = 0 # HTTP
      }

      customize_headers = []
    })
  }
}
