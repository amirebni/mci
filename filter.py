import requests
import re
import json
import base64
from urllib.parse import urlparse, parse_qs

# 🔴 اینجا لینک RAW خودتو بذار
RAW_URL = "https://raw.githubusercontent.com/punez/Repo-5/refs/heads/main/final.txt"

ALLOWED_VLESS_PORTS = {443, 2053, 2087, 2096, 8443}
ALLOWED_VMESS_WS_PORTS = {80, 443}

def is_ip(address):
    return re.match(r"^\d+\.\d+\.\d+\.\d+$", address or "") is not None


# ---------------- VLESS ----------------
def is_valid_vless(link):
    try:
        parsed = urlparse(link)
        port = parsed.port
        params = parse_qs(parsed.query)

        if not port:
            return False

        security = params.get("security", [""])[0]
        transport = params.get("type", [""])[0]
        insecure = params.get("insecure", ["1"])[0]

        if (
            security == "tls" and
            transport == "ws" and
            insecure == "0" and
            port in ALLOWED_VLESS_PORTS
        ):
            return True

        return False
    except:
        return False


# ---------------- VMESS ----------------
def decode_vmess(link):
    try:
        encoded = link.replace("vmess://", "")
        padded = encoded + "=" * (-len(encoded) % 4)
        decoded = base64.b64decode(padded).decode("utf-8")
        return json.loads(decoded)
    except:
        return None

def is_valid_vmess(link):
    data = decode_vmess(link)
    if not data:
        return False

    net = data.get("net", "")
    port = int(data.get("port", 0))
    aid = data.get("aid", "0")

    # WS سالم
    if (
        net == "ws" and
        port in ALLOWED_VMESS_WS_PORTS and
        aid == "0"
    ):
        return True

    # TCP سالم
    if (
        net == "tcp" and
        port > 1024 and
        port not in {22, 25}
    ):
        return True

    return False


# ---------------- MAIN ----------------
def main():
    response = requests.get(RAW_URL, timeout=20)
    lines = response.text.splitlines()

    filtered = []

    for line in lines:
        line = line.strip()
        if line.startswith("vless://") and is_valid_vless(line):
            filtered.append(line)
        elif line.startswith("vmess://") and is_valid_vmess(line):
            filtered.append(line)

    with open("filtered.txt", "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(item + "\n")


if __name__ == "__main__":
    main()
