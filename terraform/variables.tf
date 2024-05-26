variable "ssh_key" {
  description = "SSH key to use for the VM"
  type        = string
}

variable "template_name" {
  description = "Name of the template to clone"
  type        = string
}

variable "number_of_instances" {
  description = "Number of instances to create"
  type        = number
  default     = 1
}
