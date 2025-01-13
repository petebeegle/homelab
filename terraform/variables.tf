variable "destination_host" {
  description = "IP address of the destination host"
  type        = string
}

variable "destination_user" {
  description = "User to connect to the destination host"
  type        = string
}

variable "node_data" {
  type = object({
    controlplanes = map(object({
      node        = string
      id          = number
      memory      = number
      cores       = number
      pcie_device = string
    }))
    workers = map(object({
      node        = string
      id          = number
      memory      = number
      cores       = number
      pcie_device = string
    }))
  })
  default = {
    controlplanes = {
      "192.168.3.60" = {
        node        = "pve01"
        id          = 102
        memory      = 8192
        cores       = 2
        pcie_device = null
      },
      "192.168.3.63" = {
        node        = "pve02"
        id          = 201
        memory      = 8192
        cores       = 2
        pcie_device = null
      },
      "192.168.3.64" = {
        node        = "pve03"
        id          = 300
        memory      = 8192
        cores       = 2
        pcie_device = null
      }
    },
    workers = {
      "192.168.3.61" = {
        node        = "pve01"
        id          = 103
        memory      = 16384
        cores       = 2
        pcie_device = null
      },
      "192.168.3.62" = {
        node        = "pve02"
        id          = 200
        memory      = 16384
        cores       = 2
        pcie_device = null
      },
      "192.168.3.65" = {
        node        = "pve03"
        id          = 301
        memory      = 16384
        cores       = 2
        pcie_device = null
      },
      "192.168.3.66" = {
        node        = "pve04"
        id          = 400
        memory      = 61440
        cores       = 28
        pcie_device = "UHD_GRAPHICS_770"
      }
    }
  }
}

variable "github_token" {
  description = "GitHub token to use for the bootstrap script"
  type        = string
  sensitive   = true
}

variable "github_user" {
  description = "GitHub user to use for the bootstrap script"
  type        = string
}
