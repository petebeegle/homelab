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

variable "enable_docker_proxy" {
  description = "Whether to use a docker proxy for the cluster"
  type        = bool
  default     = false
}

variable "docker_registry" {
  description = "Credentials for authenticating to the pass-through docker registry used by the cluster"
  type = object({
    user     = string
    password = string
  })
  sensitive = true
}
