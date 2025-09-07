import socket
import ssl
from pathlib import Path
import os

from dotenv import load_dotenv

from forward_handler import ForwardingHandler

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "config", ".env"))

class TLSServerTunnel:
    """
    Tunnel TLS serveur qui écoute des connexions TLS entrantes avec authentification mutuelle.

    Attributes:
        certs_dir (Path): Répertoire contenant les certificats.
        ca_cert (Path): Chemin vers le certificat d'autorité.
        server_cert (Path): Chemin vers le certificat serveur.
    """

    def __init__(self):
        self.certs_dir = os.path.join(BASE_DIR,os.getenv("CERTS_DIR"))
        self.ca_cert = os.path.join(self.certs_dir, os.getenv("CA_CERT_NAME", "ca.pem"))
        self.server_cert = os.path.join(self.certs_dir, os.getenv("SERVER_CERT_NAME", "server.pem"))

    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        Crée un contexte SSL serveur configuré pour authentifier les clients avec leur certificat.
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.server_cert)
        context.load_verify_locations(self.ca_cert)
        context.verify_mode = ssl.CERT_REQUIRED
        return context

    def start(self, host: str = "0.0.0.0", port: int = 8443):
        """
        Lance le serveur TLS en écoute sur l'adresse spécifiée.

        Args:
            host (str): Adresse d'écoute (par défaut : 0.0.0.0).
            port (int): Port d'écoute (par défaut : 8443).
        """
        context = self._create_ssl_context()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            sock.listen(5)
            print(f"[Server] En écoute sur {host}:{port}")

            while True:
                client_sock, addr = sock.accept()
                print(f"[Server] Connexion entrante de {addr}")

                try:
                    tls_conn = context.wrap_socket(client_sock, server_side=True)
                    handler = ForwardingHandler(tls_conn)
                    handler.start()
                except ssl.SSLError as e:
                    print(f"[Server] Erreur SSL : {e}")
                except Exception as e:
                    print(f"[Server] Erreur {e}")
