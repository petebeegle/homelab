# Configure Unifi

## Prerequisites
- A cloudflare api token with the following permissions:
    `All zones - Zone:Read, DNS:Edit`
- SSH is enabled (temporarily)

## 1. Create DNS Entries
Run terraform to add DNS entries for our services:
```sh
cd terraform/environment
terraform apply -auto-approve -var="cloudflare_api_token=keep-your-secrets"
```
> [!IMPORTANT]
> Don't forget to update `cloudflare_api_token`

This will create DNS records for our Unifi service:
- `unifi`

## 2. Configure the Proxy
This service is exposed as an external service through a cilium gateway. The configuration is found [here](../kubernetes/apps/base/external).

## 3. Creating Certificates

Upload `unifi/generate_certificate.sh` to `/homes/certadmin`, then run the script for each certificate you want to create.

```sh
ssh root@192.168.1.1

./generate_certificate.sh unifi.example.com me@example.com
```
> [!NOTE]
> This script leverages the scripts found [here](https://community.ui.com/questions/UniFi-Installation-Scripts-or-UniFi-Easy-Update-Script-or-UniFi-Lets-Encrypt-or-UniFi-Easy-Encrypt-/ccbc7530-dd61-40a7-82ec-22b17f027776).

> [!IMPORTANT]
> Don't forget to update the `CF_TOKEN`!
