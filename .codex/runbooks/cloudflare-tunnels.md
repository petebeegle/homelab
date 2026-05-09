# Cloudflare Tunnels

Some Cloudflare Tunnel setup is manual and happens outside the Flux deployment.

## Login

Log in with:

```sh
cloudflared tunnel login
```

This generates a tunnel credentials JSON file in the user's Cloudflare
configuration directory. Put the contents into `Secret/tunnel-credentials`; the
pod consumes it as `credentials.json`.

## Create A Tunnel

Create a tunnel:

```sh
cloudflared tunnel create my-tunnel
```

Update the `tunnel` value in `ConfigMap/cloudflared` to match the tunnel name.

## Configure DNS

Create a proxied `CNAME` route for the tunnel:

```sh
cloudflared tunnel route dns my-tunnel example.com
```
