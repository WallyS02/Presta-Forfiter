IMAGE_NAME="wallys02/presta-forfiter:latest"
COMPOSE_URL="https://raw.githubusercontent.com/WallyS02/Presta-Forfiter/master/shop-config/docker-compose-prod.yml"
STACK_NAME="BE_188586"

docker pull $IMAGE_NAME

wget $COMPOSE_URL -O docker-compose-prod.yml

sed -i -e 's/\r$//' ./docker-compose-prod.yml

docker stack deploy -c docker-compose-prod.yml $STACK_NAME --with-registry-auth
