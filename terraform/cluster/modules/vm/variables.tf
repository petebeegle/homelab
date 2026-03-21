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
