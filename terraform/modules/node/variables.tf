variable "iso_filename" {
  description = "The filename of the ISO image to use for the VM"
  type        = string
}

variable "ipconfig0" {
  description = "The IP configuration for the VM"
  type        = string
}

variable "target_node" {
  description = "The target proxmox node for the VM"
  type        = string

  validation {
    condition     = can(regex("pve0[1-3]", var.target_node))
    error_message = "Invalid target_node value. It should be one of pve01, pve02, or pve03."
  }
}

variable "id" {
  description = "The ID of the VM"
  type        = number
}

variable "file_ready" {
  description = "The filename of the ISO image to use for the VM"
  type        = string
}
