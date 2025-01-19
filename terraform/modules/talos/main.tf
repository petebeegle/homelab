locals {
  image_name = "talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"
}


data "talos_image_factory_extensions_versions" "this" {
  talos_version = var.talos_version
  filters = {
    names = var.extensions
  }
}

resource "talos_image_factory_schematic" "this" {
  schematic = yamlencode(
    {
      customization = {
        systemExtensions = {
          officialExtensions = data.talos_image_factory_extensions_versions.this.extensions_info.*.name
        }
      }
    }
  )
}

data "talos_image_factory_urls" "this" {
  talos_version = var.talos_version
  schematic_id  = talos_image_factory_schematic.this.id
  platform      = "nocloud"
}


resource "null_resource" "this" {
  provisioner "local-exec" {
    command = "curl -o /tmp/talos-disk.iso ${data.talos_image_factory_urls.this.urls.iso}"
  }

  provisioner "file" {
    source      = "/tmp/talos-disk.iso"
    destination = "/mnt/pve/nfs/template/iso/talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"

    connection {
      type    = "ssh"
      host    = var.destination_host
      user    = var.destination_user
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

output "install_image" {
  value = data.talos_image_factory_urls.this.urls.installer
}

output "id" {
  value       = null_resource.this.id
  description = "Id generated when the provisioner is executed. Used as a dependency for other resources."
}
