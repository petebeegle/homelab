variable "target_node_name" {
  description = "Name of the node to create the VM on"
  type        = string

}

variable "vm_id" {
  description = "Id to assign to the VM"
  type        = number
}

variable "cpu_cores" {
  description = "Number of cpu cores to assign to the VM"
  type        = number
}

variable "memory" {
  description = "Amount of dedicated memory (megabytes) to assign to the VM"
  type        = number
}

variable "additional_tags" {
  description = "Additional tags to append to the VM"
  type        = list(string)

  default = []
}

variable "pci_passthrough_devices" {
  description = "Optional host PCI devices to attach to the VM. Set exactly one of id or mapping for each device."
  type = list(object({
    id       = optional(string)
    mapping  = optional(string)
    mdev     = optional(string)
    pcie     = optional(bool)
    rom_file = optional(string)
    rombar   = optional(bool)
    xvga     = optional(bool)
  }))
  default = []

  validation {
    condition = alltrue([
      for device in var.pci_passthrough_devices :
      length([
        for value in [device.id, device.mapping] : value
        if value != null && value != ""
      ]) == 1
    ])
    error_message = "Each PCI passthrough device must set exactly one non-empty value for either id or mapping."
  }

  validation {
    condition     = length(var.pci_passthrough_devices) <= 16
    error_message = "Proxmox supports at most 16 host PCI devices per VM."
  }
}

variable "network" {
  description = "Network configuration for the VM"
  type = object({
    address = string
    gateway = string
  })
}

variable "boot" {
  description = "Boot configuration for the VM"
  type = object({
    file      = string
    datastore = string
  })
}

variable "disk_size" {
  description = "Size of the boot disk in gigabytes"
  type        = number
  default     = 40
}
