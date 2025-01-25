variable "image" {
  description = "The image to use for the talos ISO"
  type = object({
    version = string
  })
}

variable "cluster" {
  description = "The cluster configuration"
  type = object({
    name     = string
    endpoint = string
  })
}

variable "cilium" {
  description = "Cilium configuration for the talos ISO"
  type = object({
    values  = string
  })
}

variable "ssh" {
  description = "SSH configuration for storing the talos ISO"
  type = object({
    user = string
    host = string
  })
}

variable "nodes" {
  description = "The nodes to create in the cluster"
  type = map(object({
    node          = string
    vm_id         = number
    memory        = number
    cores         = number
    machine_type = string
  }))
}
