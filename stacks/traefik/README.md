## Traefik Stack

Deploys traefik reverse proxy

```sh
# set secrets/env
echo "secret" > .cf_dns_api_token.secret
echo "DOMAIN=example.com" >> .env
echo "EMAIL=my.email@gmail.com" >> .env

# create acme.json for certs
mkdir letsencrypt && touch letsencrypt/acme.json && chmod -R 600 letsencrypt

# deploy stack
docker stack deploy -c stack.yml traefik

# confirm
curl -v https://traefik.lab.petebeegle.com
```