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
NAS services use public Cloudflare DNS-only (grey cloud) A records that point at
the NAS's private address, `192.168.30.99`. They are not under `lab.petebeegle.com`:
LAN DNS answers every `*.lab` name with the production cluster gateway, so a NAS
service there would be unreachable whenever production is down.

The records are set by hand in the Cloudflare dashboard (the Terraform root that
once managed them was removed):

| Name | Service |
|------|---------|
| `docker-registry.petebeegle.com` | Nexus `docker-group`, the image mirror every Talos node pulls through |
| `s3.petebeegle.com` | S3 gateway for Terraform state ([6](#6-s3-gateway-for-terraform-state)) |

## 2. Adding Reverse Proxies
Reverse proxies are set by hand in `Control Panel > Login Portal > Advanced >
Reverse Proxy`. Terraform used to create the registry entry through the
non-idempotent `SYNO.Core.AppPortal.ReverseProxy` create API, and its state had
drifted from the live entry, so it no longer manages them.

| Source (HTTPS, 443) | Destination (HTTP) |
|---------------------|--------------------|
| `docker-registry.petebeegle.com` | `localhost:8082` |
| `s3.petebeegle.com` | `localhost:7070` |

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
/homes/certadmin/generate_certificate.sh "s3.example.com" "S3 Certificate"
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

## 6. S3 gateway for Terraform state
Versity S3 Gateway serves the `terraform-state` bucket that every Terraform root
keeps its state in (decision: [docs/decisions.md](../docs/decisions.md#terraform-state-lives-in-s3-on-the-nas)).
`terraform/external/synology/s3.tf` runs it as the Container Manager project
`s3` on the `docker` share, from [`s3/docker-compose.yaml`](synology/s3/docker-compose.yaml).
It listens on the NAS loopback only (`127.0.0.1:7070`), and its objects, with
their old versions, are plain files under `/volume2/docker/s3`.

One-time setup:

1. Add the Cloudflare record for `s3.petebeegle.com` ([1](#1-create-dns-entries)).
2. Create its certificate ([3](#3-creating-certificates)), add the reverse proxy
   entry ([2](#2-adding-reverse-proxies)), and assign the certificate to it
   ([4](#4-configure-certificates)).
3. Deploy the gateway:
   ```sh
   terraform -chdir=terraform/external/synology apply
   ```
4. Store its keys in 1Password as the item `Terraform state S3` in the `cluster bootstrap` vault, without printing them:
   ```sh
   cd terraform/external/synology
   op item create --vault "cluster bootstrap" --category "API Credential" --title "Terraform state S3" \
     "username=$(terraform output -raw s3_access_key)" \
     "credential=$(terraform output -raw s3_secret_key)" \
     "hostname=https://s3.petebeegle.com" >/dev/null
   ```
5. Create the bucket and turn versioning on (safe to re-run):
   ```sh
   export AWS_ACCESS_KEY_ID=$(op read "op://cluster bootstrap/Terraform state S3/username")
   export AWS_SECRET_ACCESS_KEY=$(op read "op://cluster bootstrap/Terraform state S3/credential")
   python3 tools/terraform/state_bucket.py
   ```
   `curl -s -o /dev/null -w '%{http_code}\n' https://s3.petebeegle.com/` answers
   `403` (unsigned) once the proxy, certificate and gateway are all in place.
