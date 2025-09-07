import socket
from ssl import SSL_ERROR_SSL, SSL_ERROR_EOF
import threading

from tunnel import TLSClientTunnel
from config import ClientConfig


class Socks5ProxyHandler(threading.Thread):
    """
    Gère une connexion SOCKS5 entrante et la redirige via un tunnel TLS mTLS.

    Attributes:
        client_sock (socket.socket): Socket du client (navigateur).
        tunnel (TLSClientTunnel): Instance du tunnel TLS pour l'envoi des données.
    """

    def __init__(self, client_sock, client_addr, config: ClientConfig):
        super().__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.config = config

    def run(self):
        try:
            print(f"[SOCKS5] Nouvelle connexion depuis {self.client_addr}")

            # === Étape 1 : handshake SOCKS5 ===
            version, nmethods = self.client_sock.recv(2)
            self.client_sock.recv(nmethods)  # on ignore les méthodes proposées
            self.client_sock.sendall(b"\x05\x00")  # Réponse : SOCKS5, No Auth

            # === Étape 2 : demande de connexion ===
            data = self.client_sock.recv(4)
            if len(data) < 4 or data[0] != 5 or data[1] != 1:
                print("[SOCKS5] Requête non supportée")
                self.client_sock.close()
                return

            atyp = data[3]
            if atyp == 1:  # IPv4
                addr = socket.inet_ntoa(self.client_sock.recv(4))
            elif atyp == 3:  # domaine
                domain_len = self.client_sock.recv(1)[0]
                addr = self.client_sock.recv(domain_len).decode()
            elif atyp == 4:  # IPv6
                addr = socket.inet_ntop(socket.AF_INET6, self.client_sock.recv(16))
            else:
                print("[SOCKS5] Type d'adresse non supporté")
                self.client_sock.close()
                return

            port_bytes = self.client_sock.recv(2)
            port = int.from_bytes(port_bytes, "big")
            print(f"[SOCKS5] Requête de connexion vers {addr}:{port}")

            # === Étape 3 : réponse OK au client SOCKS5 ===
            self.client_sock.sendall(b"\x05\x00\x00\x01" + b"\x00" * 6)  # connexion acceptée

            # === Étape 4 : tunnel TLS ===
            with TLSClientTunnel().connect_raw(
                self.config.tunnel_host,
                self.config.tunnel_port
            ) as tls_sock:
                # envoyer la cible (protocole interne)
                target_line = f"{addr}:{port}\n".encode()
                tls_sock.sendall(target_line)
                self._relay(self.client_sock, tls_sock)               

        except SSL_ERROR_SLL or SSL_ERROR_EOF as e:
            print(f"[Error] : {e}")
        finally:
            self.client_sock.close()

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

        t1 = threading.Thread(target=pipe, args=(sock1, sock2, "client→tunnel[request]"), daemon=True)
        t2 = threading.Thread(target=pipe, args=(sock2, sock1, "tunnel→client[response]"), daemon=True)

        t1.start()
        t2.start()
        t1.join()
        t2.join()
