variable "target_node" {
  description = "VM target node"
  type        = string
}

variable "ssh_key" {
  description = "SSH key to use for the VM"
  type        = string
}

variable "number_of_instances" {
  description = "Number of instances to create"
  type        = number
  default     = 1
}

variable "vm_id_prefix" {
  description = "VM ID prefix"
  type        = number
}

variable "template_name" {
  description = "Name of the template to clone"
  type        = string

}
