IMAGE_NAME="wallys02/presta-forfiter:latest"
COMPOSE_URL="https://raw.githubusercontent.com/WallyS02/Presta-Forfiter/master/shop-config/docker-compose.yml"
INIT_URL="https://raw.githubusercontent.com/WallyS02/Presta-Forfiter/master/shop-config/init.sh"
STACK_NAME="BE_188586"

docker pull $IMAGE_NAME

wget $COMPOSE_URL -O docker-compose.yml

wget $INIT_URL

chmod 777 init.sh

docker stack deploy -c docker-compose.yml $STACK_NAME --with-registry-auth