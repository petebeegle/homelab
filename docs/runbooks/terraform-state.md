# Terraform state

Every Terraform root keeps its state in the bucket `terraform-state` on the
NAS S3 gateway, `https://s3.petebeegle.com`. Why it lives there is in
[decisions.md](../decisions.md#terraform-state-lives-in-s3-on-the-nas); how the
gateway is deployed is in [SYNOLOGY.md](../../scripts/SYNOLOGY.md) section 6.

| Root | Key |
|------|-----|
| `terraform/development` | `development/terraform.tfstate` |
| `terraform/production` | `production/terraform.tfstate` |
| `terraform/external/grafana` | `external/grafana/terraform.tfstate` |
| `terraform/external/synology` | `external/synology/terraform.tfstate` |
| `terraform/external/nexus` | `external/nexus/terraform.tfstate` |

`tools/terraform/tests/test_state_backends.py` holds every root to this: same
bucket, its own key, a lock, and no credentials in code.

## Credentials

The backend reads the gateway's keys from the environment. They are in the
1Password item "Terraform state S3" in the "cluster bootstrap" vault:

```sh
eval "$(op signin)"
export AWS_ACCESS_KEY_ID="$(op read 'op://cluster bootstrap/Terraform state S3/username')"
export AWS_SECRET_ACCESS_KEY="$(op read 'op://cluster bootstrap/Terraform state S3/credential')"
```

Every `init`, `plan` and `apply` needs them, including a hand run of
`tools/development/verify_branch_deploy.py` without `--ci`, which plans the
development root. Without them, `init` fails with "No valid credential sources
found". The `ci.yml` checks run `init -backend=false` and need no keys.

## Inputs: `terraform.tfvars`

Each root's `terraform.tfvars` is ignored by git and kept in 1Password as the
document "Terraform tfvars <root>" (for example "Terraform tfvars
external/grafana") in the "cluster bootstrap" vault. In a fresh clone, put them
in place without printing them:

```sh
tools/terraform/fetch_tfvars.sh            # every root
tools/terraform/fetch_tfvars.sh production # or just some
```

It keeps any `terraform.tfvars` already there and exits non-zero if a document
is missing. After changing a root's file, update its document:

```sh
op document edit "Terraform tfvars <root>" terraform/<root>/terraform.tfvars --vault "cluster bootstrap"
```

To store a root for the first time, use `op document create
terraform/<root>/terraform.tfvars --vault "cluster bootstrap" --title "Terraform
tfvars <root>" --file-name terraform.tfvars`.

## A checkout that used local state

A checkout made before the backends existed has a `.terraform/` set up for local
state and a `terraform.tfstate` that is no longer current. In each root, move
the file aside first, then initialize:

```sh
mv terraform/<root>/terraform.tfstate terraform/<root>/terraform.tfstate.pre-s3
terraform -chdir=terraform/<root> init -reconfigure
```

The order matters. While `terraform.tfstate` is there, even `init -reconfigure`
offers to copy it into the bucket, and with `-input=false` it fails with "Can't
ask approval for state migration". Never answer yes to that, and never use
`-migrate-state`: either would put the stale local file over the bucket's copy.
Keep the `.pre-s3` file until the restore proof in #486 is done, then delete it.

The synology root's `terraform output` now needs the keys too. If 1Password is
not to hand, the old file still holds them:
`jq -r '.outputs.s3_access_key.value' terraform/external/synology/terraform.tfstate.pre-s3`.

## Locks

`use_lockfile` writes `<key>.tflock` next to the state while a command runs. A
second run waits for `-lock-timeout`, then fails with `PreconditionFailed` and
names the holder. If the holder is gone (a killed run), release it:

```sh
terraform -chdir=terraform/<root> force-unlock <lock ID from the error>
```

## Old versions

The bucket is versioned. The gateway keeps earlier copies of each key, and
delete markers, as plain files under `/volume2/docker/s3/versions` on the NAS.
`terraform state pull` reads only the current one.
