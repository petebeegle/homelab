#!/bin/sh
set -eu

source_root="${SOURCE_ROOT:-/config-source}"
target_root="${TARGET_ROOT:-/config-target}"
marker="${target_root}/.homelab-config-migration-v1"
plugin_dir="plugins/SSO Authentication_4.0.0.4"

fail() {
  echo "Jellyfin config migration failed: $*" >&2
  exit 1
}

require_file() {
  path="$1"
  [ -s "${path}" ] || fail "required non-empty file is missing: ${path}"
}

validate_config_root() {
  root="$1"

  [ -d "${root}" ] || fail "config root does not exist: ${root}"
  require_file "${root}/config/system.xml"
  require_file "${root}/config/branding.xml"
  require_file "${root}/plugins/configurations/SSO-Auth.xml"
  require_file "${root}/${plugin_dir}/SSO-Auth.dll"
  require_file "${root}/${plugin_dir}/Duende.IdentityModel.dll"
  require_file "${root}/${plugin_dir}/Duende.IdentityModel.OidcClient.dll"
  require_file "${root}/${plugin_dir}/meta.json"

  database_found=false
  for database in "${root}"/data/*.db; do
    if [ -s "${database}" ]; then
      database_found=true
      break
    fi
  done
  [ "${database_found}" = "true" ] || fail "no non-empty Jellyfin database was found under ${root}/data"
}

compare_file() {
  relative_path="$1"
  source_file="${source_root}/${relative_path}"
  target_file="${target_root}/${relative_path}"

  [ -f "${target_file}" ] || fail "copied file is missing: ${target_file}"
  cmp -s "${source_file}" "${target_file}" ||
    fail "copied file does not match source: ${relative_path}"
}

compare_authentication_state() {
  compare_file "config/system.xml"
  compare_file "config/branding.xml"
  compare_file "plugins/configurations/SSO-Auth.xml"
  compare_file "${plugin_dir}/SSO-Auth.dll"
  compare_file "${plugin_dir}/Duende.IdentityModel.dll"
  compare_file "${plugin_dir}/Duende.IdentityModel.OidcClient.dll"
  compare_file "${plugin_dir}/meta.json"

  file_list="/tmp/jellyfin-config-data-files"
  find "${source_root}/data" -type f -print > "${file_list}"
  while IFS= read -r source_file; do
    relative_path="${source_file#${source_root}/}"
    compare_file "${relative_path}"
  done < "${file_list}"
  rm -f "${file_list}"
}

if [ -f "${marker}" ]; then
  validate_config_root "${target_root}"
  echo "Jellyfin local config migration already completed; target validation passed"
  exit 0
fi

validate_config_root "${source_root}"

# A target without the marker is an incomplete or untrusted attempt. Replace it
# from the stopped, read-only source rather than allowing Jellyfin to start from
# partial state.
find "${target_root}" -mindepth 1 -maxdepth 1 -exec rm -rf {} \;

cp -a "${source_root}/." "${target_root}/"
sync

validate_config_root "${target_root}"
compare_authentication_state

{
  echo "source=pvc:jellyfin-config-v2"
  echo "completed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${marker}"
sync

echo "Jellyfin config migration completed and authentication state validated"
