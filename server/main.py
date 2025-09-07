from tunnel import TLSServerTunnel
from config import ServerConfig

if __name__ == "__main__":
    config = ServerConfig()
    server = TLSServerTunnel()
    try:
        server.start(config.listen_host, config.listen_port)
    except KeyboardInterrupt:
        exit(1)

