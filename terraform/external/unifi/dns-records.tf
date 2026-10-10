locals {
  dns_records = {
    lab = {
      name  = "*.lab.petebeegle.com"
      value = "192.168.30.241"
    }
    development = {
      name  = "*.development.lab.petebeegle.com"
      value = "192.168.30.225"
    }
  }
}

resource "unifi_dns_record" "gateway_wildcards" {
  for_each = local.dns_records

  name        = each.value.name
  value       = each.value.value
  record_type = "A"
  enabled     = true
  ttl         = 300
}
