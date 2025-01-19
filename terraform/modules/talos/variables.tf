variable "talos_version" {
  description = "Talos version to use"
  type        = string

  validation {
    condition     = can(regex("v[0-9]+\\.[0-9]+\\.[0-9]+", var.talos_version))
    error_message = "Talos version must be in the format v1.2.3"
  }
}

variable "destination_user" {
  description = "User to connect to the destination host"
  type        = string
}

variable "destination_host" {
  description = "Host to connect to"
  type        = string
}

variable "extensions" {
  description = "List of extensions to include in the Talos image"
  type        = list(string)
}
