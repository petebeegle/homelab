variable "iso_filename" {
  description = "The filename of the ISO image to use for the VM"
  type        = string
}

variable "ip" {
  description = "The IP configuration for the VM"
  type        = string
}

variable "target_node" {
  description = "The target proxmox node for the VM"
  type        = string

  validation {
    condition     = can(regex("pve*", var.target_node))
    error_message = "Invalid target_node value. It should start with pve."
  }
}

variable "vm_id" {
  description = "The ID of the VM"
  type        = number
}

variable "memory" {
  description = "The memory size of the VM"
  type        = number
}

variable "cores" {
  description = "The number of cores for the VM"
  type        = number
}
