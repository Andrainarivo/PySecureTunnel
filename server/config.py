from pathlib import Path
import os

from utils.configLoader import ConfigLoader


class ServerConfig:
    """
    Représente la configuration du serveur proxy TLS.

    Attributes:
        listen_host (str): IP d'écoute du serveur.
        listen_port (int): Port d'écoute du serveur.
    """

    def __init__(self):
        loader = ConfigLoader(
            yaml_path=os.path.join(Path(__file__).resolve().parent, "config", "server_config.yaml")
        )
        config = loader.load()

        self.listen_host = config.get("server", {}).get("listen_host")
        self.listen_port = int(config.get("server", {}).get("listen_port"))
