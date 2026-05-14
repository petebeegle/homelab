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

## Route Public Apps

Public Cloudflare hostnames should enter Kubernetes through `gateway/public`.
Cloudflared forwards public traffic to the public Gateway over HTTP, and the app-owned `HTTPRoute` selects the backend Service. Do not point cloudflared ingress rules directly at app Services.

For each public hostname:

1. Add a cloudflared ingress rule that sends the hostname to the public Gateway:

   ```yaml
   - hostname: app.petebeegle.com
     service: http://cilium-gateway-public.gateway.svc.cluster.local:80
   ```

2. Add an app-owned `HTTPRoute` with `parentRefs` set to `gateway/public` and `sectionName: http-gateway`.
3. Keep the final cloudflared fallback rule as `service: http_status:404`.
