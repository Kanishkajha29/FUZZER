import socket
import ssl
import whois
import subprocess
from OpenSSL import crypto

def get_network_map(url):
    try:
        ip = socket.gethostbyname(url)
        open_ports = []
        for port in [80, 443, 22, 21, 8080, 3306]:  # Add other ports to check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return {"ip": ip, "open_ports": open_ports}
    except Exception as e:
        return f"Error gathering network map: {e}"

def get_whois_info(url):
    try:
        domain = whois.whois(url)
        return domain.text
    except Exception as e:
        return f"Error gathering WHOIS information: {e}"

def get_ssl_info(url):
    try:
        hostname = url
        port = 443
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
                subject = x509.get_subject()
                issuer = x509.get_issuer()

                return {
                    "subject": str(subject),
                    "issuer": str(issuer),
                    "expiration": x509.get_notAfter().decode('utf-8')
                }
    except Exception as e:
        return f"Error gathering SSL information: {e}"
