import socket
import threading
from utils.logger import get_logger

logger = get_logger("SERVER") 


class ForwardingHandler(threading.Thread):
    """
    Gère une connexion TLS entrante et la redirige vers la cible.
    """

    def __init__(self, client_sock: socket.socket):
        super().__init__()
        self.client_sock = client_sock

    def run(self):
        try:
            # Lire la ligne cible + garder ce qui suit dans le buffer
            target_line, leftover = self._recv_until_newline(self.client_sock)
            if not target_line:
                logger.debug("Erreur : aucune adresse cible reçue.")
                self.client_sock.close()
                return

            target_host, target_port = self._parse_target(target_line)
            logger.info(f"Requête de connexion vers {target_host}:{target_port}")

            # Connexion réelle vers la cible
            target_sock = socket.create_connection((target_host, target_port))
            logger.info("Connexion établie")

            # Si des données de la requête sont déjà arrivées, on les forward immédiatement
            if leftover:
                logger.info(f"Données leftover à forward : {leftover}")
                target_sock.sendall(leftover)

            # Relais bidirectionnel
            self._relay(self.client_sock, target_sock)

        except Exception as e:
            pass
        finally:
            try:
                self.client_sock.close()
            except Exception:
                pass

    def _recv_until_newline(self, sock: socket.socket) -> tuple[str, bytes]:
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(1)
            if not chunk:
                break
            data += chunk
        # tout ce qui reste dans le buffer TLS est déjà lu par recv,
        # donc on retourne aussi le surplus
        line, _, rest = data.partition(b"\n")
        return line.decode().strip(), rest

    def _parse_target(self, line: str) -> tuple[str, int]:
        if ":" not in line:
            raise ValueError(f"Adresse invalide reçue : {line}")
        host, port_str = line.strip().split(":")
        return host, int(port_str)

    def _relay(self, sock1, sock2):
        def pipe(src, dst, label):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception as e:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        t1 = threading.Thread(target=pipe, args=(sock1, sock2, "tunnel→cible[request]"), daemon=True)
        t2 = threading.Thread(target=pipe, args=(sock2, sock1, "cible→tunnel[response]"), daemon=True)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

