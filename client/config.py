from pathlib import Path
import os

from utils.configLoader import ConfigLoader

class ClientConfig:
    """
    Représente la configuration complète du client proxy.

    Attributs:
        host (str): Adresse du serveur TLS distant.
        port (int): Port du serveur TLS.
        proxy_type (str): Type de proxy local (http, socks5...).
        proxy_port (int): Port d'écoute du proxy local.
    """

    def __init__(self):
        loader = ConfigLoader(
            yaml_path=os.path.join(Path(__file__).resolve().parent, "config", "client_config.yaml")
        )
        config = loader.load()

        self.tunnel_host = config.get("tunnel", {}).get("remote_host")
        self.tunnel_port = int(config.get("tunnel", {}).get("remote_port", 8443))
        self.proxy_type = config.get("proxy", {}).get("type", "socks5")
        self.proxy_host = config.get("proxy", {}).get("listen_host")
        self.proxy_port = int(config.get("proxy", {}).get("listen_port", 1080))
        # self.socks5_user = config.get("auth", {}).get("socks5_user")
        # self.socks5_pass = config.get("auth", {}).get("socks5_pass")
