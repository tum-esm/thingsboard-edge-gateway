import os
import docker

from modules.git_client import GatewayGitClient
from utils.paths import ACROPOLIS_GATEWAY_GIT_PATH, ACROPOLIS_COMMUNICATION_DATA_PATH

CONTROLLER_CONTAINER_NAME = "acropolis_edge_controller"
CONTROLLER_IMAGE_PREFIX = "acropolis-edge-controller-"

class GatewayDockerClient:
    def __init__(self):
        self.docker_client = docker.from_env()

    # Singleton pattern
    def __new__(cls):
        if not hasattr(cls, 'instance') or cls.instance is None:
            print("[DOCKER-CLIENT] Initializing GatewayDockerClient")
            cls.instance = super(GatewayDockerClient, cls).__new__(cls)
        return cls.instance
    instance = None

    def is_edge_running(self):
        containers = self.docker_client.containers.list()
        for container in containers:
            if container.name == CONTROLLER_CONTAINER_NAME:
                return container.attrs["State"]["Running"]

    def is_image_available(self, image_tag):
        for image in self.docker_client.images.list():
            if image_tag in image.tags:
                return True
        return False

    def get_edge_version(self):
        if self.is_edge_running():
            containers = self.docker_client.containers.list()
            for container in containers:
                if container.name == CONTROLLER_CONTAINER_NAME:
                    version = container.attrs["Config"]["Image"].split("-")[-1]
                    if version.__len__() > 0 and (
                            version[0] == "v" or version.__len__() == 40
                    ):
                        return version

    def stop_edge(self):
        if self.is_edge_running():
            containers = self.docker_client.containers.list()
            for container in containers:
                if container.name == CONTROLLER_CONTAINER_NAME:
                    container.stop(timeout=60)
                    print("[DOCKER-CLIENT] Stopped Acropolis Edge Controller container")
        else:
            print("[DOCKER-CLIENT] Acropolis Edge Controller container is not running")

    def prune_containers(self):
        self.docker_client.containers.prune()
        print("[DOCKER-CLIENT] Pruned containers")

    def start_edge(self, version):
        if self.is_edge_running():
            current_version = self.get_edge_version()
            if current_version is None or current_version != version:
                self.stop_edge()
                self.start_edge(version)
            else:
                print("[DOCKER-CLIENT] Software already running with version " + version)
            return

        # edge container is not running
        # check if the image is available already, if not build it
        if not self.is_image_available(CONTROLLER_IMAGE_PREFIX + version + ":latest"):
            print("[DOCKER-CLIENT] Image not available, building image first...")
            GatewayGitClient().execute_fetch()
            commit_hash = GatewayGitClient().get_commit_from_hash_or_tag(version)
            if commit_hash is None:
                print("[DOCKER-CLIENT][FATAL] Unable to get commit hash for version " + version)
                return
            print("[DOCKER-CLIENT] Building image for commit " + commit_hash)

            if GatewayGitClient().execute_reset_to_commit(commit_hash) \
                and GatewayGitClient().get_current_commit() == commit_hash:
                print("[DOCKER-CLIENT] Successfully reset to commit " + commit_hash)
            else:
                print("[DOCKER-CLIENT][FATAL] Unable to reset to commit " + commit_hash)
                return
            self.docker_client.images.build(
                path=os.path.join(os.path.dirname(ACROPOLIS_GATEWAY_GIT_PATH), "software/controller"),
                dockerfile="./docker/Dockerfile",
                tag=CONTROLLER_IMAGE_PREFIX + version + ":latest"
            )
            print("[DOCKER-CLIENT] Built image for commit " + commit_hash + " with tag " + CONTROLLER_IMAGE_PREFIX + version)

        # remove old containers and start the new one
        self.prune_containers()
        self.docker_client.containers.run(
            CONTROLLER_IMAGE_PREFIX + version,
            detach=True,
            name=CONTROLLER_CONTAINER_NAME,
            restart_policy={
                "Name": "always",
                "MaximumRetryCount": 0
            },
            privileged=True,
            network_mode="host",
            environment={
                "ACROPOLIS_COMMUNICATION_DATA_PATH": "/root/data",
                "ACROPOLIS_LOG_TO_CONSOLE": 1
            },
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
                ACROPOLIS_COMMUNICATION_DATA_PATH: {
                    "bind": "/root/data",
                    "mode": "rw"
                },
            }
        )
        print("[DOCKER-CLIENT] Started Acropolis Edge container with version " + version)