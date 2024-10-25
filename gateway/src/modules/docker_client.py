import docker


class GatewayDockerClient:
    def __init__(self):
        self.docker_client = docker.from_env()

    def is_edge_running(self):
        containers = self.docker_client.containers.list()
        for container in containers:
            if container.name == "acropolis_edge":
                return container.attrs["State"]["Running"]


    def start_edge(self):
        if not self.is_edge_running():
            #self.docker_client.containers.run("acropolis_edge", detach=True)
            print("[DOCKER-CLIENT] Started Acropolis Edge container")
        else:
            print("[DOCKER-CLIENT] Acropolis Edge container is already running")