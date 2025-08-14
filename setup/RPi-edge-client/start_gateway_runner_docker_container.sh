docker container stop thingsboard_edge_gateway
docker container prune -f
docker run -d \
 --restart unless-stopped \
 --privileged \
 -v /:/host \
 --name thingsboard_edge_gateway \
 --env TEG_GATEWAY_DIR=/home/pi/thingsboard-edge-gateway \
 --env TEG_DATA_PATH=/home/pi/teg-data \
 --env TEG_GATEWAY_GIT_PATH=/home/pi/thingsboard-edge-gateway/.git \
 --env TEG_CONTROLLER_LOGS_PATH=/home/pi/teg-data/controller-logs \
 --env THINGSBOARD_PROVISION_DEVICE_KEY=... \
 --env THINGSBOARD_PROVISION_DEVICE_SECRET=... \
 --env THINGSBOARD_DEVICE_NAME=$(hostname) \
 thingsboard-edge-gateway-runner:latest --tb-host thingsboard.esm.ei.tum.de --tb-port 8843
