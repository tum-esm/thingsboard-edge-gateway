"""Docker runtime management for the Edge Gateway controller.

This module provides the :class:`~modules.docker_client.GatewayDockerClient`, a thin
wrapper around the Docker Engine API used by the Edge Gateway to manage the
*controller* container.

Responsibilities
----------------
- Detect whether the controller container is running and determine its version.
- Start/stop the controller container in a controlled way.
- Build controller images from a Git tag or commit hash if the image is not available.
- Publish ThingsBoard OTA-related software state updates via MQTT (``sw_state``).

The controller is deployed as a Docker container (``teg_controller``) with images
tagged as ``teg-controller-<version>:latest``. Versions may be Git tags (e.g. ``v1.2.3``)
or full commit hashes.

Notes
-----
- This client is implemented as a process-level singleton to avoid repeated Docker
  client initialization.
- The implementation assumes host networking and a privileged container, as required
  for the deployed Raspberry Pi environment.

"""

import datetime
import os
from time import sleep
from typing import Any, Optional

import docker
from docker import DockerClient
from docker.types import LogConfig

from modules.git_client import GatewayGitClient
from modules.logging import debug, info, warn, error
from modules.mqtt import GatewayMqttClient
from utils.paths import CONTROLLER_GIT_PATH, GATEWAY_DATA_PATH, CONTROLLER_LOGS_PATH, CONTROLLER_DATA_PATH, \
    CONTROLLER_DOCKERCONTEXT_PATH, CONTROLLER_DOCKERFILE_PATH

CONTROLLER_CONTAINER_NAME: str = "teg_controller"
CONTROLLER_IMAGE_PREFIX: str = "teg-controller-"

singleton_instance: Optional["GatewayDockerClient"] = None

class GatewayDockerClient:
    """Manage the controller Docker container for an Edge Gateway device.

    The gateway and controller are intentionally separated: the Edge Gateway remains
    stable while controller versions can be updated independently (e.g. via OTA
    packages in ThingsBoard).

    This class wraps Docker operations (list, stop, run, build) and integrates with
    the gateway’s Git and MQTT clients to support automated controller updates.

    Attributes
    ----------
    last_launched_version:
      Cached version string of the last successfully launched controller.
    docker_client:
      Docker SDK client instance created via :func:`docker.from_env`, or ``None`` if
      Docker is unavailable.

    """
    last_launched_version: Optional[str] = None
    docker_client: Optional[DockerClient] = None

    def __init__(self) -> None:
        global singleton_instance
        if singleton_instance is None:
            debug("[DOCKER-CLIENT] Initializing GatewayDockerClient")
            super().__init__()
            singleton_instance = self
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                error("[DOCKER-CLIENT] Failed to initialize GatewayDockerClient: {}".format(e))
                self.docker_client = None

    # Singleton pattern
    def __new__(cls: Any) -> Any:
        global singleton_instance
        if singleton_instance is not None:
            return singleton_instance
        return super(GatewayDockerClient, cls).__new__(cls)

    def get_last_launched_controller_version(self) -> Optional[str]:
        """Return the last launched controller version.

        The value is cached in-memory and persisted in
        ``$GATEWAY_DATA_PATH/last_launched_controller_version.txt``. If the file is not
        available, the environment variable ``TEG_DEFAULT_CONTROLLER_VERSION`` is used
        as a fallback.

        Returns:
          The version tag/commit hash, or ``None`` if unknown.
        """
        if self.last_launched_version is not None:
            return self.last_launched_version
        # read controller version from file
        try:
            with open(os.path.join(GATEWAY_DATA_PATH, "last_launched_controller_version.txt"), "r") as file:
                last_launched_controller_version = file.read()
                self.last_launched_version = last_launched_controller_version
                return last_launched_controller_version
        except:
            default_version = os.environ.get("TEG_DEFAULT_CONTROLLER_VERSION")
            if default_version is not None:
                return default_version
            return None

    def set_last_launched_controller_version(self, last_launched_controller_version: str):
        """Persist the last launched controller version.

        Args:
          last_launched_controller_version: Git tag or commit hash to store.
        """
        self.last_launched_version = last_launched_controller_version
        # write to file
        try:
            with open(os.path.join(GATEWAY_DATA_PATH, "last_launched_controller_version.txt"), "w") as file:
                file.write(last_launched_controller_version)
        except Exception as e:
            error("[DOCKER-CLIENT] Failed to write last launched controller version: {}".format(e))

    def is_controller_running(self) -> bool:
        """Check whether the controller container is running.

        Returns:
          ``True`` if the container exists and is running, otherwise ``False``.
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] is_controller_running: Docker client not initialized")
            return False
        containers = self.docker_client.containers.list()
        for container in containers:
            if container.name == CONTROLLER_CONTAINER_NAME:
                return container.attrs["State"]["Running"]
        return False

    def is_image_available(self, image_tag: str) -> bool:
        """Check whether a Docker image tag exists locally.

        Args:
          image_tag: Full Docker image tag to look up (e.g. ``teg-controller-v1.0.0:latest``).

        Returns:
          ``True`` if the image tag exists locally, otherwise ``False``.
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] is_image_available: Docker client not initialized")
            return False
        for image in self.docker_client.images.list():
            if image_tag in image.tags:
                return True
        return False

    def get_controller_version(self) -> Optional[str]:
        """Return the controller version inferred from the running container image.

        Returns:
          The Git tag/commit hash parsed from the image name, or ``None`` if the
          controller is not running or the version cannot be determined.
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] get_controller_version: Docker client not initialized")
            return None
        if self.is_controller_running():
            containers = self.docker_client.containers.list()
            for container in containers:
                if container.name == CONTROLLER_CONTAINER_NAME:
                    version = container.attrs["Config"]["Image"].split("-")[-1]
                    if version.__len__() > 0 and (version[0] == "v"
                                                  or version.__len__() == 40):
                        if version.endswith(":latest"):
                            version = version[:-7]
                        return version
        return None

    def get_edge_startup_timestamp_ms(self) -> Optional[int]:
        """Return the controller container start time as Unix milliseconds.

        Returns:
          Start timestamp in milliseconds (UTC) if the controller is running, else ``None``.
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] get_edge_startup_timestamp_ms: Docker client not initialized")
            return None
        if self.is_controller_running():
            containers = self.docker_client.containers.list()
            for container in containers:
                if container.name == CONTROLLER_CONTAINER_NAME:
                    return int(
                        datetime.datetime.strptime(container.attrs["State"]["StartedAt"][:-4], "%Y-%m-%dT%H:%M:%S.%f" )
                        .replace(tzinfo=datetime.timezone.utc)
                        .timestamp() * 1000
                    )
        return None

    def stop_controller(self) -> None:
        """Stop the running controller container (if any).

        This stores the currently running controller version as the last-launched
        version before stopping the container.

        Returns:
          None
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] stop_controller: Docker client not initialized")
            return None
        if self.is_controller_running():
            containers = self.docker_client.containers.list()
            for container in containers:
                if container.name == CONTROLLER_CONTAINER_NAME:
                    running_controller_version = self.get_controller_version()
                    if running_controller_version is not None:
                        self.set_last_launched_controller_version(running_controller_version)
                    info("[DOCKER-CLIENT] Stopping controller container...")
                    container.stop(timeout=60)
                    info("[DOCKER-CLIENT] Stopped controller container")
        else:
            info("[DOCKER-CLIENT] Controller container is not running")

    def prune_containers(self) -> None:
        """Remove stopped containers to keep the Docker environment clean."""
        if self.docker_client is None:
            error("[DOCKER-CLIENT] prune_containers: Docker client not initialized")
            return None
        self.docker_client.containers.prune()
        info("[DOCKER-CLIENT] Pruned containers")

    def start_controller_safely(self, version_to_launch: str):
        """Start the controller and suppress unexpected exceptions.

        Args:
          version_to_launch: Git tag or commit hash to run.
        """
        try:
            self.start_controller(version_to_launch)
        except Exception as e:
            warn("[DOCKER-CLIENT] Failed to start controller: {}".format(e))
            
    def start_controller(self, version_to_launch: str) -> None:
        """Start the controller container for a given version.

        If the requested version is already running, the method is a no-op. If the
        required image is not available locally, the controller repository is fetched,
        reset to the referenced commit, and a Docker image is built from the local
        Docker context.

        During the update lifecycle, the method publishes OTA-related states via MQTT
        (e.g. ``DOWNLOADING``, ``DOWNLOADED``, ``UPDATING``, ``UPDATED``).

        Args:
          version_to_launch: Git tag (e.g. ``v1.0.0``) or full commit hash.

        Returns:
          None
        """
        if self.docker_client is None:
            error("[DOCKER-CLIENT] start_controller: Docker client not initialized")
            return None
        if self.is_controller_running():
            running_controller_version = self.get_controller_version()
            if running_controller_version != version_to_launch:
                self.stop_controller()
                self.start_controller(version_to_launch)
            else:
                info("[DOCKER-CLIENT] Software already running with version " + version_to_launch)
                self.set_last_launched_controller_version(running_controller_version)
            return

        image_tag : str = CONTROLLER_IMAGE_PREFIX + version_to_launch + ":latest"

        # edge container is not running
        # check if the image is available already, if not build it
        if not self.is_image_available(image_tag):
            error("[DOCKER-CLIENT] Image '" + image_tag + "' not available")
            info("[DOCKER-CLIENT] Building image for version '" + version_to_launch + "'")
            GatewayMqttClient().publish_sw_state(version_to_launch, "DOWNLOADING")
            GatewayGitClient().execute_fetch()
            commit_hash = GatewayGitClient().get_commit_from_hash_or_tag(version_to_launch)
            if commit_hash is None:
                error("[DOCKER-CLIENT] Unable to get commit hash for version '" + version_to_launch + "'")
                return
            info("[DOCKER-CLIENT] Building image for commit " + commit_hash)

            if GatewayGitClient().execute_reset_to_commit(commit_hash) \
                and GatewayGitClient().get_current_commit() == commit_hash:
                info("[DOCKER-CLIENT] Successfully reset to commit " + commit_hash)
            else:
                error("[DOCKER-CLIENT] Unable to reset to commit " + commit_hash)
                return
            GatewayMqttClient().publish_sw_state(version_to_launch, "DOWNLOADED")
            self.docker_client.images.build(
                path=CONTROLLER_DOCKERCONTEXT_PATH,
                dockerfile=CONTROLLER_DOCKERFILE_PATH,
                tag=CONTROLLER_IMAGE_PREFIX + version_to_launch + ":latest"
            )
            info("[DOCKER-CLIENT] Built image for commit " + commit_hash + " with tag " + CONTROLLER_IMAGE_PREFIX + version_to_launch)

        GatewayMqttClient().publish_sw_state(version_to_launch, "UPDATING")
        # remove old containers and start the new one
        self.prune_containers()
        self.docker_client.containers.run(
            image_tag,
            detach=True,
            name=CONTROLLER_CONTAINER_NAME,
            restart_policy={
                "MaximumRetryCount": 3,
                "Name": "on-failure"
            },
            log_config=LogConfig(type=LogConfig.types.JSON, config={
                "max-size": "10m",
                "max-file": "5"
            }),
            privileged=True,
            network_mode="host",
            volumes={
                "/bin/vcgencmd": {
                    "bind": "/bin/vcgencmd",
                    "mode": "ro"
                },
                "/bin/uptime": {
                    "bind": "/bin/uptime",
                    "mode": "ro"
                },
                "/bin/pigs": {
                    "bind": "/bin/pigs",
                    "mode": "ro"
                },
                CONTROLLER_DATA_PATH: {
                    "bind": "/root/data",
                    "mode": "rw"
                },
                CONTROLLER_LOGS_PATH: {
                    "bind": "/root/logs",
                    "mode": "rw"
                },
            }
        )
        self.set_last_launched_controller_version(version_to_launch)

        GatewayMqttClient().publish_sw_state(version_to_launch, "UPDATED")
        info("[DOCKER-CLIENT] Started container with version '" + version_to_launch + "'")