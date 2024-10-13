variable "nas_ip" {
  description = "IP address of the NAS"
  type        = string
  default     = "192.168.3.3"
}

variable "nas_user" {
  description = "User to connect to the NAS"
  type        = string
  default     = "ansible"
}

variable "nas_port" {
  description = "Port to connect to the NAS"
  type        = string
  default     = "2200"
}

variable "node_data" {
  type = object({
    controlplanes = map(object({
      node = string
      id   = number
    }))
    workers = map(object({
      node = string
      id   = number
    }))
  })
  default = {
    controlplanes = {
      "192.168.3.60" = {
        node = "pve01"
        id   = 102
      }
    },
    workers = {
      "192.168.3.61" = {
        node = "pve01"
        id   = 103
      },
      "192.168.3.62" = {
        node = "pve02"
        id   = 200
      }
    }
  }
}
