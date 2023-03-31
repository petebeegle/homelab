## Homepage stack

Deploys homepage dashboard

### Usage

```sh
# set secrets/env
echo "STACK_HOMEPAGE_DOMAIN=example.com" >> .env
export $(cat .env)

# deploy stack
docker stack deploy -c stack.yml homepage

# confirm
curl -v https://homepage.example.com
```

### Configurations

#### STACK_HOMEPAGE_DOMAIN
The domain host to route to