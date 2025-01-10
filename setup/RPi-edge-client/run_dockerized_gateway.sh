docker container stop acropolis_edge_gateway
docker container prune -f
docker run -d \
 --restart unless-stopped \
 --privileged \
 -v /:/host \
 --name acropolis_edge_gateway \
 --env ACROPOLIS_GATEWAY_DIR=/home/pi/acropolis/acropolis-edge/software/gateway \
 --env ACROPOLIS_DATA_PATH=/home/pi/acropolis/data \
 --env ACROPOLIS_GATEWAY_GIT_PATH=/home/pi/acropolis/acropolis-edge/.git \
 --env ACROPOLIS_CONTROLLER_LOGS_PATH=/home/pi/acropolis/logs \
 --env THINGSBOARD_PROVISION_DEVICE_KEY=... \
 --env THINGSBOARD_PROVISION_DEVICE_SECRET=... \
 --env THINGSBOARD_DEVICE_NAME=$(hostname) \
 acropolis-gateway-runner:latest --tb-host thingsboard.esm.ei.tum.de --tb-port 8843
