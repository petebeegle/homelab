locals {
  cluster_cidr = "192.168.3.240/28"
}

data "cloudflare_zone" "this" {
  zone_id = "462b7a48654756f890133f60191c2cd5"
}

resource "cloudflare_dns_record" "nexus" {
  type    = "A"
  content = "192.168.3.27"
  name    = "nexus"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Nexus record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "synology" {
  type    = "A"
  content = "192.168.3.27"
  name    = "nas"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Synology record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "docker" {
  type    = "A"
  content = "192.168.3.27"
  name    = "docker-registry"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Docker Registry record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "pve01" {
  type    = "A"
  content = "192.168.3.242"
  name    = "pve01"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Proxmox Node 1 record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "pve02" {
  type    = "A"
  content = "192.168.3.242"
  name    = "pve02"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Proxmox Node 2 record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "pve03" {
  type    = "A"
  content = "192.168.3.242"
  name    = "pve03"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Proxmox Node 3 record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "pve04" {
  type    = "A"
  content = "192.168.3.242"
  name    = "pve04"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Proxmox Node 4 record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "unifi" {
  type    = "A"
  content = "192.168.1.1"
  name    = "unifi"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Unifi controller record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

resource "cloudflare_dns_record" "lab" {
  for_each = toset([for i in range(1, pow(2, (32 - tonumber(split("/", local.cluster_cidr)[1]))) - 1) : cidrhost(local.cluster_cidr, i)])

  type    = "A"
  content = each.key
  name    = "*.lab"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Cluster record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}

data "http" "my_public_ip" {
  url = "https://ifconfig.co/json"
  request_headers = {
    Accept = "application/json"
  }
}

resource "cloudflare_dns_record" "arda" {
  type    = "A"
  content = jsondecode(data.http.my_public_ip.response_body).ip
  name    = "arda"
  ttl     = 1 # automatic

  comment = "[Terraform Managed] Arda record"
  proxied = false

  zone_id = data.cloudflare_zone.this.zone_id
}
