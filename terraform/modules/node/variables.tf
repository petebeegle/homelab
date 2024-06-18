variable "target_node" {
  description = "Target proxmox node to deploy to"
  type        = string
}

variable "ssh_key" {
  description = "SSH key to use for the VM"
  type        = string
}

variable "ip_config" {
  description = "IP configuration for the VM"
  type        = string
}

variable "gateway" {
  description = "Gateway for the VM"
  type        = string

}

variable "image" {
  description = "Image to use for the VM"
  type        = string
}
