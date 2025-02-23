#!/bin/bash

# This script is designed to create certificates on the synology NAS.
#
# Usage:
#   ./generate_certificate.sh [arguments]
#
# Arguments:
#   [argument1]       Domain of the certificate to create
#
# Examples:
#   ./generate_certificate.sh [argument1]
#
# Notes:
#   - Ensure you have the necessary permissions to execute the script.

ACME_SH_DIR="/usr/local/share/acme.sh"
CERT_OWNER="certadmin"
if [ -z "$1" ]; then
	echo "Usage: $0 <domain>"
	exit 1
fi

# Description of the certificate to create
if [ -z "$2" ]; then
	echo "Usage: $0 <certificate_name>"
	exit 1
fi

DOMAIN="$1"
export SYNO_CERTIFICATE="$2"

# Username to auth to synology
export SYNO_USERNAME="$CERT_OWNER"


# Whether to create the certificate
# 0 = No
# 1 = Yes
export SYNO_Create=1

if [ -z "$CF_TOKEN" ]; then
  echo "Error: CF_TOKEN environment variable is not set."
  exit 1
fi

if [ -z "$SYNO_PASSWORD" ]; then
  echo "Error: SYNO_PASSWORD environment variable is not set."
  exit 1
fi

install_acme_sh() {
	if [ -d "$ACME_SH_DIR" ]; then
		echo "acme.sh is already installed at $ACME_SH_DIR"
		return
	fi

	wget -O /tmp/acme.sh.zip https://github.com/acmesh-official/acme.sh/archive/master.zip
	sudo 7z x -o/usr/local/share /tmp/acme.sh.zip
	sudo mv /usr/local/share/acme.sh-master/ /usr/local/share/acme.sh
	sudo chown -R "$CERT_OWNER" "$ACME_SH_DIR/"
}

install_acme_sh
cd /usr/local/share/acme.sh
./acme.sh --issue -d "$DOMAIN" --dns dns_cf --home $PWD --server letsencrypt
./acme.sh -d "$DOMAIN" --deploy --deploy-hook synology_dsm --home $PWD
