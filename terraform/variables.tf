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

variable "bootstrap_new_cluster" {
  description = "Bootstrap a new cluster"
  type        = bool
  default     = false
}

variable "node_data" {
  type = object({
    controlplanes = map(object({
      node   = string
      id     = number
      memory = number
      cores  = number
    }))
    workers = map(object({
      node   = string
      id     = number
      memory = number
      cores  = number
    }))
  })
  default = {
    controlplanes = {
      "192.168.3.60" = {
        node   = "pve01"
        id     = 102
        memory = 8192
        cores  = 2
      },
      "192.168.3.63" = {
        node   = "pve02"
        id     = 201
        memory = 8192
        cores  = 2
      },
      "192.168.3.64" = {
        node   = "pve03"
        id     = 300
        memory = 8192
        cores  = 2
      }
    },
    workers = {
      "192.168.3.61" = {
        node   = "pve01"
        id     = 103
        memory = 16384
        cores  = 2
      },
      "192.168.3.62" = {
        node   = "pve02"
        id     = 200
        memory = 16384
        cores  = 2
      },
      "192.168.3.65" = {
        node   = "pve03"
        id     = 301
        memory = 16384
        cores  = 2
      }
    }
  }
}
