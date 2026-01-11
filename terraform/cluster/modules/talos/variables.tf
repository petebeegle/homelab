variable "image" {
  description = "Information about the image to use for the VM"
  type = object({
    version = string
  })
}

variable "cluster" {
  description = "Information about the cluster to join"
  type = object({
    name     = string
    endpoint = string
  })
}

variable "cilium" {
  description = "Information about the cilium configuration"
  type = object({
    values = string
  })
}

variable "nfs_server" {
  description = "Information about the nfs server configuration"
  type = object({
    name             = string
    user             = string
    host             = string
    destination_path = string
  })
}

variable "nodes" {
  description = "The nodes to create in the cluster"
  type = map(object({
    node         = string
    vm_id        = number
    memory       = number
    cores        = number
    machine_type = string
    disk_size    = number
  }))
}

variable "docker_image_proxy" {
  description = "Configuration for the docker image proxy used by the cluster"
  type = object({
    enabled = bool
    registry = optional(object({
      user     = string
      password = string
    }))
  })
  sensitive = true
  default = {
    enabled  = false
    registry = null
  }
}
