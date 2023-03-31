## Traefik Stack

Deploys traefik reverse proxy

### Usage

```sh
# set secrets/env
echo "secret" > .cf_dns_api_token.secret
echo "STACK_TRAEFIK_DOMAIN=example.com" >> .env
echo "STACK_TRAEFIK_EMAIL=my.email@gmail.com" >> .env
export $(cat .env)

# create acme.json for certs
mkdir letsencrypt && touch letsencrypt/acme.json
chmod -R 600 letsencrypt

# deploy stack
docker stack deploy -c stack.yml traefik

# confirm
curl -v https://traefik.lab.petebeegle.com
```

### Configurations

#### STACK_TRAEFIK_DOMAIN
The domain host to route to

#### STACK_TRAEFIK_EMAIL
The email to resolve a certificate