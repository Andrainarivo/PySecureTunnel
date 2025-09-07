import socket
import ssl
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "config", ".env"))

class TLSClientTunnel:
    """
    Tunnel TLS client qui se connecte à un serveur TLS avec authentification mutuelle.

    Attributes:
        certs_dir (Path): Répertoire contenant les certificats.
        ca_cert (Path): Chemin vers le certificat d'autorité.
        client_cert (Path): Chemin vers le certificat client.
    """

    def __init__(self):
        self.certs_dir = os.path.join(BASE_DIR, os.getenv("CERTS_DIR"))
        self.ca_cert = os.path.join(self.certs_dir, os.getenv("CA_CERT_NAME", "ca.pem"))
        self.client_cert = os.path.join(self.certs_dir, os.getenv("CLIENT_CERT_NAME", "client.pem"))

    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        Crée un contexte SSL client configuré avec vérification du serveur et certificat client.
        """
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(self.ca_cert)
        context.load_cert_chain(certfile=self.client_cert)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False  # facultatif si CN/IP pas vérifié
        return context

    def connect_raw(self, host: str, port: int):
        """
        Établit un tunnel TLS vers le serveur (sans envoyer la cible).
        L'envoi de l'adresse cible se fait dans Socks5ProxyHandler.

        Args:
            host (str): Hôte du serveur TLS.
            port (int): Port du serveur TLS.
            target_addr (tuple): Adresse cible à atteindre (via le proxy serveur).

        Returns:
            socket.socket: Connexion TLS prête à être utilisée.
        """
        context = self._create_ssl_context()
        raw_sock = socket.create_connection((host, port))
        tls_sock = context.wrap_socket(raw_sock, server_hostname=host)

        return tls_sock