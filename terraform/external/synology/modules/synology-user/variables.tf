variable "synology_host" {
  description = "Synology NAS host URL"
  type        = string
}

variable "username" {
  description = "Username to create"
  type        = string
}

variable "password" {
  description = "Password for the user"
  type        = string
  sensitive   = true
}

variable "description" {
  description = "User description"
  type        = string
  default     = ""
}

variable "disabled" {
  description = "Whether the user is disabled"
  type        = bool
  default     = false
}

variable "email" {
  description = "User email address"
  type        = string
  default     = ""
}

variable "expired" {
  description = "Whether the user account is expired"
  type        = bool
  default     = false
}

variable "groups" {
  description = "List of groups to add the user to"
  type        = list(string)
  default     = []
}

variable "create" {
  description = "Whether to create the user"
  type        = bool
  default     = true
}
