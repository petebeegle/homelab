locals {
  image_name = "talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"
}

data "talos_image_factory_urls" "this" {
  talos_version = var.talos_version
  schematic_id  = "ce4c980550dd2ab1b17bbf2b08801c7eb59418eafe8f279833297925d67c7515"
  platform      = "nocloud"
}

resource "null_resource" "this" {
  triggers = {
    on_url_change = data.talos_image_factory_urls.this.urls.iso
  }

  provisioner "local-exec" {
    command = "curl -o /tmp/talos-disk.iso ${data.talos_image_factory_urls.this.urls.iso}"
  }

  provisioner "file" {
    source      = "/tmp/talos-disk.iso"
    destination = "/mnt/pool/proxmox-data/template/iso/talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"

    connection {
      type    = "ssh"
      user    = var.destination_user
      host    = var.destination_host
      port    = var.destination_port
      timeout = "30s"
    }
  }

  provisioner "local-exec" {
    command = "sleep 5"
  }
}

output "filename" {
  value = local.image_name
}

output "id" {
  value       = null_resource.this.id
  description = "Id generated when the provisioner is executed. Used as a dependency for other resources."
}
