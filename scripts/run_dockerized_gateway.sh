docker container stop thingsboard-edge-gateway-runner
docker container prune -f
docker run -d \
 --restart unless-stopped \
 --privileged \
 -v /:/host \
 --net=host --pid=host --ipc=host \
 --name thingsboard-edge-gateway-runner \
 --env-file ../.env \
 thingsboard-edge-gateway-runner:latest


