## 🛡️ PySecureTunnel

### Local SOCKS5 Proxy → mTLS Tunnel → Remote Server → TCP Target

PySecureTunnel is a lightweight, secure, end-to-end encrypted tunneling system that:

- exposes a local SOCKS5 proxy,
- encapsulates all traffic in a mutually authenticated TLS tunnel,
- forwards decrypted data to a remote server,
- which connects to the final TCP service.

It acts as a micro-VPN, but with:

+ no routing changes,
+ no kernel modules,
+ fully user-space,
+ per-application control.

## ✨ Features (Current Version)
### ✔️ SOCKS5 Local Proxy

- Full SOCKS5 handshake (no authentication yet)
- Domain, IPv4, IPv6 support
- Multi-threaded client handling

### ✔️ Encrypted Tunnel (mTLS)

+ Mutual TLS authentication

+ Server & Client certificates validated against a shared CA

+ TLS termination on server side

+ Encrypted forwarding channel

### ✔️ Remote Server Forwarder

* Receives decrypted tunnel traffic

* Extracts target host/port

* Forwards to the requested TCP endpoint

* Full duplex bidirectional forwarding

### ✔️ Unified Configuration Layer

- YAML configuration files

- .env for sensitive paths

- Automatic merge via ConfigLoader

## 🔧 Installation

### Install dependencies
```bash
pip install -r requirements.txt
```

### 🔐 Certificate Generation (OpenSSL or certs.py)

#### OpenSSL

1. **Create a CA**
```bash
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem \
  -subj "/C=US/ST=None/O=PySecureTunnel/OU=CA/CN=PySecureTunnel-CA"
```

2. **Create Server Certificate**
```bash
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr \
  -subj "/C=US/ST=None/O=PySecureTunnel/OU=Server/CN=server"
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out server.pem -days 3650 -sha256
```

3. **Create Client Certificate**
```bash
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr \
  -subj "/C=US/ST=None/O=PySecureTunnel/OU=Client/CN=client"
openssl x509 -req -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out client.pem -days 3650 -sha256
```

4. **File placement**

Server:
```
server/certs/ca.pem
server/certs/server.pem
```
Client:
```
client/certs/ca.pem
client/certs/client.pem
```


## ⚙️ Configuration

#### **Client**: `client/config/client_config.yaml`
```yaml
proxy:
  type: socks5
  listen_host: "127.0.0.1"
  listen_port: 1080

tunnel:
  remote_host: "127.0.0.1"
  remote_port: 8443
```

#### **Server**: `server/config/server_config.yaml`
```yaml
listen_host: "0.0.0.0"
listen_port: 8443
```


##  ▶️ Running the System

#### **Start the server**
```bash
cd server
python main.py
```

#### **Start the client (local SOCKS5)**
```bash
cd client
python main.py
```

#### **Test through the tunnel**
```bash
curl -x socks5h://127.0.0.1:1080 http://example.com
```

### 🧪 Basic Test

Start a HTTP test server:
```bash
python3 -m http.server 8080
```

Forward through the encrypted tunnel:
```bash
curl -x socks5h://127.0.0.1:1080 http://127.0.0.1:8080
```

## Security Notes

#### Current version:

- mTLS enforced

- Local SOCKS5 only

- No user authentication yet

- No WAN exposure by default

- No routing manipulation

#### Roadmap (future):

- SOCKS5 username/password

- Option to disable client cert auth (TLS only)

- Traffic integrity checks (SYN/FIN log, packet stats)

- Auto health-check on tunnel startup
