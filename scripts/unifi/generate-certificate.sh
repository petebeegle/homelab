#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <domain>"
	exit 1
fi

if [ -z "$2" ]; then
	echo "Usage: $0 <email>"
	exit 1
fi


FQDN="$1"
EMAIL="$2"
CF_CONFIG=~/.secrets/certbot/cloudflare.ini

if [ -z "$CF_TOKEN" ]; then
  echo "Error: CF_TOKEN environment variable is not set."
  exit 1
fi

echo "dns_cloudflare_api_token = $CF_TOKEN" > $CF_CONFIG

curl -sO https://get.glennr.nl/unifi/extra/unifi-easy-encrypt.sh

bash unifi-easy-encrypt.sh --dns-provider cloudflare --dns-challenge --fqdn $FQDN --email $EMAIL --dns-provider-credentials $CF_CONFIG --server-ip 192.168.1.1
