#!/usr/bin/env bash
set -euo pipefail

readonly TERRAFORM_DOCS_VERSION="0.23.0"
readonly TERRAFORM_DOCS_ARCHIVE="terraform-docs-v${TERRAFORM_DOCS_VERSION}-linux-amd64.tar.gz"
readonly TERRAFORM_DOCS_URL="https://github.com/terraform-docs/terraform-docs/releases/download/v${TERRAFORM_DOCS_VERSION}/${TERRAFORM_DOCS_ARCHIVE}"

temp_dir=""
terraform_docs_bin=""

cleanup() {
  if [[ -n "${temp_dir}" && -d "${temp_dir}" ]]; then
    rm -rf "${temp_dir}"
  fi
}
trap cleanup EXIT

fail() {
  echo "update-terraform-docs: $*" >&2
  exit 1
}

terraform_docs_version_matches() {
  local bin="$1"
  local version_output

  version_output="$("${bin}" --version 2>/dev/null || true)"
  [[ "${version_output}" == *" v${TERRAFORM_DOCS_VERSION} "* ]]
}

download_terraform_docs() {
  command -v curl >/dev/null 2>&1 ||
    fail "curl is required to download terraform-docs v${TERRAFORM_DOCS_VERSION}"
  command -v tar >/dev/null 2>&1 ||
    fail "tar is required to extract terraform-docs v${TERRAFORM_DOCS_VERSION}"

  temp_dir="$(mktemp -d)"
  local archive_path="${temp_dir}/${TERRAFORM_DOCS_ARCHIVE}"

  echo "update-terraform-docs: downloading terraform-docs v${TERRAFORM_DOCS_VERSION}" >&2
  curl --fail --location --retry 5 --retry-delay 5 --retry-all-errors \
    -sSLo "${archive_path}" \
    "${TERRAFORM_DOCS_URL}" ||
    fail "failed to download ${TERRAFORM_DOCS_URL}"
  tar -xzf "${archive_path}" -C "${temp_dir}" terraform-docs ||
    fail "failed to extract ${TERRAFORM_DOCS_ARCHIVE}"
  chmod +x "${temp_dir}/terraform-docs"

  terraform_docs_version_matches "${temp_dir}/terraform-docs" ||
    fail "downloaded terraform-docs is not v${TERRAFORM_DOCS_VERSION}"
  terraform_docs_bin="${temp_dir}/terraform-docs"
}

select_terraform_docs() {
  if command -v terraform-docs >/dev/null 2>&1; then
    local candidate
    candidate="$(command -v terraform-docs)"

    if terraform_docs_version_matches "${candidate}"; then
      terraform_docs_bin="${candidate}"
      return
    fi

    echo "update-terraform-docs: ${candidate} is not v${TERRAFORM_DOCS_VERSION}; using pinned download" >&2
  else
    echo "update-terraform-docs: terraform-docs not found; using pinned download" >&2
  fi

  download_terraform_docs
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" ||
  fail "must be run from inside the homelab git repository"
cd "${repo_root}"

select_terraform_docs

mapfile -d '' readmes < <(
  find terraform -path '*/README.md' -type f -print0 |
    sort -z
)

if [[ "${#readmes[@]}" -eq 0 ]]; then
  echo "update-terraform-docs: no Terraform README files found"
  exit 0
fi

updated=0
for readme in "${readmes[@]}"; do
  if ! grep -q '<!-- BEGIN_TF_DOCS -->' "${readme}"; then
    continue
  fi

  module_dir="$(dirname "${readme}")"
  "${terraform_docs_bin}" markdown table \
    --output-file README.md \
    --output-mode inject \
    "${module_dir}"
  updated=$((updated + 1))
done

if [[ "${updated}" -eq 0 ]]; then
  echo "update-terraform-docs: no generated Terraform README files found"
else
  echo "update-terraform-docs: refreshed ${updated} Terraform README files"
fi
