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

variable "ssh" {
  description = "Information about the ssh configuration"
  type = object({
    user = string
    host = string
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
