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
    condition     = can(regex("pve0[1-4]", var.target_node))
    error_message = "Invalid target_node value. It should be one of pve01, pve02, pve03, or pve04."
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

variable "memory" {
  description = "The memory size of the VM"
  type        = number
}

variable "cores" {
  description = "The number of cores for the VM"
  type        = number
}

variable "pcie_device" {
  description = "Optional: The PCI device ID to attach to the VM"
  type        = string
  default     = null
}
