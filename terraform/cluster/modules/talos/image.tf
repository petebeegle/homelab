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

resource "null_resource" "this" {

  provisioner "local-exec" {
    command = "curl -L ${data.talos_image_factory_urls.this.urls.iso} > /tmp/talos-disk.iso"
  }

  provisioner "file" {
    source      = "/tmp/talos-disk.iso"
    destination = "/mnt/pve/nfs/template/iso/talos-${data.talos_image_factory_urls.this.talos_version}-${data.talos_image_factory_urls.this.platform}-${data.talos_image_factory_urls.this.architecture}.iso"

    connection {
      type    = "ssh"
      host    = var.ssh.host
      user    = var.ssh.user
      timeout = "30s"
    }
  }

  provisioner "local-exec" {
    command = "sleep 5"
  }
}
