import requests
from urllib.parse import urlparse, parse_qs
import ipaddress

# پورت‌های SSL مجاز
SSL_PORTS = {443, 8443, 2053, 2087, 2096}

# رنج‌های IPv4 مربوط به Cloudflare
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
    if not url.startswith("vless://"):
        return 0

    try:
        parsed = urlparse(url)
        host = parsed.hostname

        try:
            port = parsed.port
        except:
            return 0  # اگر پورت خراب بود رد شود

        query = parse_qs(parsed.query)

    except:
        return 0

    score = 0

    security = query.get("security", [""])[0]
    typ = query.get("type", [""])[0]
    insecure = query.get("insecure", ["1"])[0]
    sni = query.get("sni", [""])[0]
    fp = query.get("fp", [""])[0]
    alpn = query.get("alpn", [""])[0]

    # امتیازدهی

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

    if port and port in SSL_PORTS:
        if port == 443:
            score += 2
        else:
            score += 1

    # بررسی Cloudflare
    if host:
        try:
            ipaddress.ip_address(host)
            if is_cloudflare_ip(host):
                score += 3
        except:
            pass

    return score


def fetch_sources():
    all_configs = set()

    with open("sources.txt") as f:
        sources = [line.strip() for line in f if line.strip()]

    for src in sources:
        try:
            print(f"Fetching: {src}")
            r = requests.get(src, timeout=20)
            lines = r.text.splitlines()

            for line in lines:
                line = line.strip()
                if line:
                    all_configs.add(line)

        except Exception as e:
            print(f"Failed: {src}")

    return list(all_configs)


def main():
    configs = fetch_sources()
    print(f"\nTotal unique configs: {len(configs)}\n")

    scored = []

    for conf in configs:
        s = score_config(conf)
        if s >= 8:
            scored.append((s, conf))

    scored.sort(reverse=True)

    print("🔥 GOLD CONFIGS:\n")

    with open("gold.txt", "w") as f:
        for s, conf in scored:
            print(f"[{s}] {conf}")
            f.write(conf + "\n")

    print(f"\nSaved {len(scored)} configs to gold.txt")


if __name__ == "__main__":
    main()
