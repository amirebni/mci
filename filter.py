import requests
import re
from urllib.parse import urlparse, parse_qs
import ipaddress

RAW_URL = "https://raw.githubusercontent.com/punez/Repo-5/refs/heads/main/final.txt"

SSL_PORTS = {443, 8443, 2053, 2087, 2096}

# Cloudflare IPv4 ranges (خلاصه شده)
CF_RANGES = [
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22"
]

def is_cloudflare_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        for net in CF_RANGES:
            if ip_obj in ipaddress.ip_network(net):
                return True
    except:
        pass
    return False

def score_config(url):
    score = 0

    if not url.startswith("vless://"):
        return 0

    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    query = parse_qs(parsed.query)

    security = query.get("security", [""])[0]
    typ = query.get("type", [""])[0]
    insecure = query.get("insecure", ["1"])[0]
    sni = query.get("sni", [""])[0]
    fp = query.get("fp", [""])[0]
    alpn = query.get("alpn", [""])[0]

    if security == "tls":
        score += 3

    if typ == "ws":
        score += 3
    elif typ == "xhttp":
        score += 2

    if insecure == "0":
        score += 2

    if sni:
        score += 2

    if fp == "chrome":
        score += 1

    if "http/1.1" in alpn:
        score += 1

    if port in SSL_PORTS:
        score += 2 if port == 443 else 1

    # اگر IP مستقیم بود
    if host:
        try:
            ipaddress.ip_address(host)
            if is_cloudflare_ip(host):
                score += 3
        except:
            pass

    return score

def main():
    response = requests.get(RAW_URL, timeout=20)
    lines = response.text.splitlines()

    scored = []

    for line in lines:
        s = score_config(line.strip())
        if s >= 8:
            scored.append((s, line.strip()))

    scored.sort(reverse=True)

    print("\n🔥 GOLD CONFIGS:\n")
    for s, conf in scored:
        print(f"[Score {s}] {conf}")

if __name__ == "__main__":
    main()
