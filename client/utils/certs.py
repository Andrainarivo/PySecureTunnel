from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "config", ".env"))

class CertificateManager:
    """
    Gère la génération de l'autorité de certification (CA),
    ainsi que les certificats serveur et client, avec RSA 4096 bits.
    """

    def __init__(self):
        self.certs_dir = os.path.join(BASE_DIR, os.getenv("CERTS_DIR"))
        self.ca_cert_path = os.path.join(self.certs_dir, os.getenv("CA_CERT_NAME", "ca.pem"))
        # self.server_cert_path = self.certs_dir / os.getenv("SERVER_CERT_NAME", "server.pem")
        self.client_cert_path = os.path.join(self.certs_dir, os.getenv("CLIENT_CERT_NAME", "client.pem"))
        self.key_size = 4096
        self.validity_days = 365

        self.certs_dir.mkdir(parents=True, exist_ok=True)

    def generate_key(self) -> rsa.RSAPrivateKey:
        """Génère une clé privée RSA."""
        return rsa.generate_private_key(public_exponent=65537, key_size=self.key_size)

    def save_pem(self, cert: x509.Certificate, key: rsa.RSAPrivateKey, path: Path):
        """Enregistre le certificat et sa clé dans un seul fichier PEM."""
        with open(path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

    def create_ca(self) -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """Crée un certificat d'autorité racine (CA) avec SubjectKeyIdentifier et KeyUsage."""
        ca_key = self.generate_key()
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"MG"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ShadowLANProxy"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"ShadowLAN Root CA"),
        ])
        cert_builder = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.validity_days * 2)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False
        ).add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True, # requis pour CA (droit de signer d'autres certificats)
                crl_sign=True,
                encipher_only=False,
                decipher_only=False
            ), critical=True
        )

        cert = cert_builder.sign(ca_key, hashes.SHA256())

        self.save_pem(cert, ca_key, self.ca_cert_path)
        return cert, ca_key

    def create_signed_cert(self, common_name: str, ca_cert: x509.Certificate,
                           ca_key: rsa.RSAPrivateKey, output_path: Path):
        """Crée un certificat signé par la CA avec CN donné et avec l'extension AKI (Authority Key Identifier)."""
        key = self.generate_key()
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"MG"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ShadowLAN"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        cert_builder = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False
        )

        cert = cert_builder.sign(ca_key, hashes.SHA256())

        self.save_pem(cert, key, output_path)

    def generate_all(self):
        """Génère la CA, le certificat serveur et client."""
        #ca_cert, ca_key = self.create_ca()
        #self.create_signed_cert("ShadowLAN Proxy Server", ca_cert, ca_key, self.server_cert_path)
        self.create_signed_cert("ShadownLAN Proxy Client", ca_cert, ca_key, self.client_cert_path)
        print("[Certs] Certificat client a été généré avec succès.")
