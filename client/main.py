import socket

from socks5 import Socks5ProxyHandler
from config import ClientConfig

def start_socks5_proxy(config: ClientConfig):
    listen_addr = config.proxy_host
    listen_port = config.proxy_port
    print(f"[SOCKS5] En écoute sur {listen_addr}:{listen_port}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((listen_addr, listen_port))
        server_sock.listen()

        while True:
            client_sock, client_addr = server_sock.accept()
            handler = Socks5ProxyHandler(client_sock, client_addr, config)
            handler.start()

if __name__ == "__main__":
    try:
        config = ClientConfig()
        start_socks5_proxy(config)
    except KeyboardInterrupt:
        exit(1)

