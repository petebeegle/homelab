variable "ssh_key" {
  description = "SSH key to use for the VM"
  type        = string
}

variable "network_config" {
  description = "Network configurations for the kubernetes cluster"
  type = object({
    gateway = string
    ips     = set(string)
  })
}

variable "image" {
  description = "Image to use for the VM"
  type        = string
}
