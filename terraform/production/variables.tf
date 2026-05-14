variable "github_token" {
  description = "GitHub token to use for the bootstrap script"
  type        = string
  sensitive   = true
}

variable "github_user" {
  description = "GitHub user to use for the bootstrap script"
  type        = string
}

variable "docker_user" {
  description = "Docker user for authenticating to the pass-through docker registry"
  type        = string
}

variable "docker_password" {
  description = "Docker password for authenticating to the pass-through docker registry"
  type        = string
  sensitive   = true
}

variable "nodes" {
  description = "List of nodes to create in the cluster"
  type = list(object({
    address      = string
    node         = string
    vm_id        = number
    memory       = number
    cores        = number
    machine_type = string
    disk_size    = number
  }))

  validation {
    condition = alltrue([
      for node in var.nodes : can(regex("^pve", node.node))
    ])
    error_message = "The node field must start with 'pve' (e.g., pve01, pve02, etc.)."
  }

  validation {
    condition = alltrue([
      for node in var.nodes : contains(["controlplane", "worker"], node.machine_type)
    ])
    error_message = "The machine_type must be either 'controlplane' or 'worker'."
  }

  validation {
    condition = alltrue([
      for node in var.nodes : node.cores >= 1
    ])
    error_message = "The cores must be at least 1."
  }

  validation {
    condition = alltrue([
      for node in var.nodes : can(cidrhost("${node.address}/24", 0)) && can(regex("^192\\.168\\.30\\.", node.address))
    ])
    error_message = "All keys in the nodes map must be valid IP addresses from the 192.168.30.0/24 subnet."
  }

  validation {
    condition = length([
      for node in var.nodes : node.vm_id
      ]) == length(distinct([
        for node in var.nodes : node.vm_id
    ]))
    error_message = "All vm_id values must be unique across nodes."
  }

  validation {
    condition = length([
      for node in var.nodes : node if node.machine_type == "controlplane"
    ]) >= 1
    error_message = "At least one controlplane node is required."
  }
}

variable "talos_version" {
  description = "The version of Talos to use for the cluster"
  type        = string
}
