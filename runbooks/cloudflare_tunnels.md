# Cloudflare Tunnels

In order to configure cloudflare tunnels, there are some manual steps aside from simply deploying the repo:

## Login

Log in with the following command
```sh
cloudflared tunnel login
```
This will generate a configuration file at `~/.cloudflared/<guid>.json`. The contents of this file are dumped into `Secret/tunnel-credentials` and exposed to the pod as `credentials.json`.

## Create a tunnel
Create a tunnel:
```sh
cloudflared tunnel create my-tunnel
```
Make sure to update/configure the `tunnel` configuration in `ConfigMap/cloudflared` to match the tunnel name given above.

## Configure DNS
Finally, configure a `CNAME` entry to proxy to the created tunnel
```sh
cloudflared tunnel route dns my-tunnel example.com
```
