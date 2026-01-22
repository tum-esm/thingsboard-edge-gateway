Setup
=====

Environment Variables
---------------------

Edit -env file to set up basic configuration of edge-gateway.


"TEG_DATA_PATH"
buffered logs, archive, config, communication queue

"TEG_CONTROLLER_DATA_PATH"
data path for controller specific data

(Optional) "TEG_CONTROLLER_LOGS_PATH"
defaults to "TEG_CONTROLLER_DATA_PATH" if not set
path where controller logs are stored

"TEG_CONTROLLER_GIT_PATH"
points to the git repository for the controller that was setup by the operator

(Optional) "TEG_CONTROLLER_DOCKERCONTEXT_PATH"
defaults to "TEG_CONTROLLER_GIT_PATH"/docker

(Optional) "TEG_CONTROLLER_DOCKERFILE_PATH"
path where the dockerfile to build the controller image is located + filename
is relative to "TEG_CONTROLLER_DOCKERCONTEXT_PATH"
defaults to "./Dockerfile"

Prequesites
- Setup ThingsBoard Server
- Setup device profiles in ThingsBoard + Link https://thingsboard.io/docs/user-guide/device-profiles/
- Configure Name + Transport Type: MQTT + Provisioning Strategy: Secret Provisioning "Allow to create new devices"
- Configure provisioning secret in edge-gateway (Set as environment variable in.env)

"THINGSBOARD_HOST"
"THINGSBOARD_PORT"
"THINGSBOARD_PROVISION_DEVICE_KEY"
"THINGSBOARD_PROVISION_DEVICE_SECRET"


- Set desired hostname in OS configuration

(Optional) "THINGSBOARD_DEVICE_NAME"=$(hostname)



Device Provisioning
-------------------

- Initial start of gateway + docker commands or link
- Device name will match hostname