# variable "image" {
#   description = "Information about the image to use for the VM"
#   type = object({
#     version = string
#   })
# }

# variable "cluster" {
#   description = "Information about the cluster to join"
#   type = object({
#     name     = string
#     endpoint = string
#   })
# }

# variable "cilium" {
#   description = "Information about the cilium configuration"
#   type = object({
#     values = string
#   })
# }

# variable "nfs_server" {
#   description = "Information about the nfs server configuration"
#   type = object({
#     name             = string
#     user             = string
#     host             = string
#     destination_path = string
#   })
# }

# variable "nodes" {
#   description = "The nodes to create in the cluster"
#   type = map(object({
#     node         = string
#     vm_id        = number
#     memory       = number
#     cores        = number
#     machine_type = string
#     disk_size    = number
#   }))
# }

# variable "docker_image_proxy" {
#   description = "Configuration for the docker image proxy used by the cluster"
#   type = object({
#     enabled = bool
#     registry = optional(object({
#       user     = string
#       password = string
#     }))
#   })
#   sensitive = true
#   default = {
#     enabled  = false
#     registry = null
#   }
# }

variable "talos_version" {
  description = "The version of Talos to use for the cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for Talos-generated component images and bootstrap Cilium template compatibility"
  type        = string
}

variable "control_nodes" {
  description = "List of nodes to compose the cluster control plane"
  type        = set(string)
}

variable "worker_nodes" {
  description = "List of nodes to compose the cluster worker plane"
  type        = set(string)
}

variable "node_labels" {
  description = "Kubernetes node labels to apply through Talos machine.nodeLabels, keyed by node address."
  type        = map(map(string))
  default     = {}
}

variable "cluster" {
  description = "Information about the cluster to join"
  type = object({
    name     = string
    endpoint = string
  })

  validation {
    condition     = can(regex("^https://.+$", var.cluster.endpoint))
    error_message = "Cluster endpoint must use https."
  }

  validation {
    condition     = can(regex("^.+:6443$", var.cluster.endpoint))
    error_message = "Cluster endpoint must have port 6443."
  }
}

variable "docker_registry" {
  description = "Docker registry credentials"
  type = object({
    user     = string
    password = string
  })
  sensitive = true
}

variable "installer" {
  description = "Installer url to load"
  type        = string
}

variable "allow_scheduling_on_control_planes" {
  description = "Allow Kubernetes workloads to schedule on control-plane nodes"
  type        = bool
  default     = false
}

variable "cilium_operator_replicas" {
  description = "Concrete Cilium operator replica count to render into bootstrap Helm values"
  type        = number

  validation {
    condition     = var.cilium_operator_replicas >= 1
    error_message = "Cilium operator replicas must be at least 1."
  }
}

variable "kubeconfig_output_path" {
  description = "Optional path where the generated kubeconfig should be written"
  type        = string
  default     = null
}

variable "talosconfig_output_path" {
  description = "Optional path where the generated talosconfig should be written"
  type        = string
  default     = null
}
