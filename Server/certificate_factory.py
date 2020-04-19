import datetime
from OpenSSL import crypto
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

CERT_FILE = "server.cert"

KEY_FILE = "server.key"

class CertificateFactory:

    @classmethod
    def create_self_signed_cert(cls, key_size, hostname, days_valid):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, key_size)
        private_key = pkey.to_cryptography_key()

        builder = x509.CertificateBuilder()

        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ]))
        one_day = datetime.timedelta(1, 0, 0)
        builder = builder.not_valid_before(datetime.datetime.today())
        builder = builder.not_valid_after(datetime.datetime.today() + (one_day * days_valid))
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(private_key.public_key())
        builder = builder.add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName(hostname)]
            ),
            critical=False
        )
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        )
        certificate = builder.sign(
            private_key=private_key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        certificate_file = open(CERT_FILE, 'wb')
        certificate_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
        key_file = open(KEY_FILE, 'wb')
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
