# Check if the user already exists
data "external" "check_user" {
  program = ["bash", "-c", <<-EOT
    response=$(curl -sk "${var.synology_host}/webapi/entry.cgi" \
      -d "api=SYNO.API.Auth" \
      -d "version=3" \
      -d "method=login" \
      -d "account=${var.username}" \
      -d "passwd=${var.password}" \
      -d "session=test" \
      -d "format=cookie" 2>&1)

    if echo "$response" | grep -q '"success":true'; then
      echo '{"exists":"true"}'
    else
      echo '{"exists":"false"}'
    fi
  EOT
  ]
}

resource "synology_api" "user" {
  count = var.create && data.external.check_user.result.exists == "false" ? 1 : 0

  api     = "SYNO.Core.User"
  method  = "create"
  version = 1

  parameters = {
    name        = var.username
    password    = var.password
    description = var.description
    disable     = var.disabled ? 1 : 0
    email       = var.email
    expired     = var.expired ? 1 : 0
  }
}

resource "synology_api" "user_groups" {
  for_each = var.create && data.external.check_user.result.exists == "false" ? toset(var.groups) : []

  api     = "SYNO.Core.Group.Member"
  method  = "add"
  version = 1

  parameters = {
    group = each.value
    user  = var.username
  }

  depends_on = [synology_api.user]
}
