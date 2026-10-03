variable "unifi" {
  description = "UniFi provider connection details supplied from an untracked local tfvars file, or omitted when using provider-supported environment variables such as UNIFI_API and UNIFI_API_KEY."
  type = object({
    api_url        = optional(string)
    username       = optional(string)
    password       = optional(string)
    site           = optional(string, "default")
    allow_insecure = optional(bool, true)
  })
  default   = {}
  sensitive = true
}
