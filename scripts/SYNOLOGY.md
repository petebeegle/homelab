# Configure Synology
1. [Prerequisites](#prerequisites)
2. [Create DNS Entries](#1-create-dns-entries)
3. [Adding Reverse Proxies](#2-adding-reverse-proxies)
4. [Creating Certificates](#3-creating-certificates)
    - [Creating a user](#creating-a-user)
    - [Create a Certificate](#create-a-certificate)
5. [Configure Certificates](#4-configure-certificates)
6. [Certificate Renewal](#5-certificate-renewal)

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

This will create DNS records for our Synology services:
- `nas`
- `nexus`
- `docker-registry`

## 2. Adding Reverse Proxies
Run the following:
```sh
cd /workspaces/homelab/terraform/external/synology
terraform init
terraform apply -auto
```

## 3. Creating Certificates

### Creating a user
1. Navigate to `Control Panel > User & Group` and click `Create`
2. Name the user `certadmin` and generate a password
3. Under `Permissions`, mark all items as `No Access`
4. Under `Applications`, mark all items as `Deny`

### Create a Certificate

1. Upload `generate_certificate.sh` to `/homes/certadmin`, then run the script for each certificate you want to create:

```sh
ssh certadmin@synology

export SYNO_PASSWORD="..."
export CF_TOKEN="..."
/homes/certadmin/generate_certificate.sh "nas.example.com" "Synology Certificate"
/homes/certadmin/generate_certificate.sh "nexus.example.com" "Nexus Certificate"
/homes/certadmin/generate_certificate.sh "docker-registry.example.com" "Docker Registry Certificate"
```
> [!IMPORTANT]
> Don't forget to update the `SYNO_PASSWORD` and `CF_TOKEN`!

## 4. Configure Certificates
1. Navigate to `Control Panel > Security > Certificates` and verify that your new `nas.example.com` certificate exists with the supplied description `Synology Certificate`.
2. In `Settings`, choose the `nas.example.com` Certificate for the `nas.example.com` Service.
3. Repeat mapping for other services (such as `nexus` or `docker-registry`).

## 5. Certificate Renewal
Navigate to `Control Panel > Task Scheduler` and `Create` a new `Scheduled Task > User-defined script` with the following options:

| Setting           | Value               |
|-------------------|---------------------|
| Task              | Renew Certificate   |
| User              | `certadmin`         |

> [!IMPORTANT]
>For setting the schedule itself, it's important to know that Lets-Encrypt issues 3-month certs, so a 3 month schedule offset by a week or 2 should be sufficient.

> [!NOTE]
>For `User-defined script`, see [renew_certificate.sh](scripts/synology/renew_certificate.sh). This script will renew all certificates.
