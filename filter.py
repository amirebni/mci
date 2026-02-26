import requests
from urllib.parse import urlparse, parse_qs

RAW_URL = "https://raw.githubusercontent.com/punez/Repo-5/refs/heads/main/final.txt"

ALLOWED_PORTS = {443, 8443, 2096, 2087, 2053, 2083}

def is_valid_vless(link):
    try:
        if not link.startswith("vless://"):
            return False

        parsed = urlparse(link)
        port = parsed.port
        params = parse_qs(parsed.query)

        security = params.get("security", [""])[0]
        transport = params.get("type", [""])[0]
        insecure = params.get("insecure", ["0"])[0]
        sni = params.get("sni", [""])[0]

        # حالت CDN Safe
        if (
            security == "tls" and
            transport in {"ws", "xhttp", "grpc"} and
            port in ALLOWED_PORTS and
            insecure == "0" and
            sni != ""
        ):
            return True

        # حالت Low Port Escape
        if (
            security == "none" and
            transport == "tcp" and
            port is not None and
            port < 100
        ):
            return True

        return False

    except:
        return False


def main():
    response = requests.get(RAW_URL, timeout=15)
    lines = response.text.splitlines()

    filtered = [line.strip() for line in lines if is_valid_vless(line.strip())]

    with open("filtered.txt", "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(item + "\n")


if __name__ == "__main__":
    main()
