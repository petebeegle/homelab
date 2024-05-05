variable "iso_name" {
  description = "Name of the ISO file"
  type        = string
  validation {
    condition     = can(regex("^.*\\.iso$", var.iso_name))
    error_message = "The file name must end with .iso"
  }
}

variable "target_nodes" {
  description = "Comma separated list of target nodes"
  type        = string
}