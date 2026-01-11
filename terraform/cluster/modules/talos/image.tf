locals {
  image_name = "talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"
}

data "talos_image_factory_extensions_versions" "this" {
  talos_version = var.image.version
}

resource "talos_image_factory_schematic" "this" {
  schematic = file("${path.module}/image/schematic.yaml")
}

data "talos_image_factory_urls" "this" {
  talos_version = var.image.version
  schematic_id  = talos_image_factory_schematic.this.id
  platform      = "nocloud"
}

resource "null_resource" "image" {
  triggers = {
    talos_version = data.talos_image_factory_urls.this.talos_version
    schematic_id  = talos_image_factory_schematic.this.id
  }

  provisioner "local-exec" {
    command = <<-EOT
      if [ ! -f /tmp/${local.image_name} ]; then
        curl -L ${data.talos_image_factory_urls.this.urls.iso} -o /tmp/${local.image_name}
      else
        echo 'Image ${local.image_name} already exists, skipping download'
      fi
    EOT
  }

  provisioner "file" {
    source      = "/tmp/${local.image_name}"
    destination = "${var.nfs_server.destination_path}/${local.image_name}"

    connection {
      type    = "ssh"
      host    = var.nfs_server.host
      user    = var.nfs_server.user
      timeout = "30s"
    }
  }

  provisioner "local-exec" {
    command = "sleep 5"
  }
}
