import requests
import re
from urllib.parse import urlparse, parse_qs

RAW_URL = "PASTE_YOUR_RAW_LINK_HERE"

ALLOWED_PORTS = {443, 8443, 2096, 2087, 2053}

def is_ip(address):
    return re.match(r"^\d+\.\d+\.\d+\.\d+$", address) is not None

def is_valid_vless(link):
    try:
        if not link.startswith("vless://"):
            return False

        parsed = urlparse(link)
        server = parsed.hostname
        port = parsed.port
        params = parse_qs(parsed.query)

        if not server or not port:
            return False

        # حذف IP مستقیم
        if is_ip(server):
            return False

        security = params.get("security", [""])[0]
        transport = params.get("type", [""])[0]
        insecure = params.get("insecure", ["1"])[0]
        sni = params.get("sni", [""])[0]
        host = params.get("host", [""])[0]

        # فقط الگوی Cloudflare-like
        if (
            security == "tls" and
            transport == "ws" and
            insecure == "0" and
            port in ALLOWED_PORTS and
            sni != "" and
            host != ""
        ):
            return True

        return False

    except:
        return False


def main():
    response = requests.get(RAW_URL, timeout=20)
    lines = response.text.splitlines()

    filtered = [line.strip() for line in lines if is_valid_vless(line.strip())]

    with open("filtered.txt", "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(item + "\n")


if __name__ == "__main__":
    main()
