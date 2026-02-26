import requests
from urllib.parse import urlparse
import ipaddress
import socket

# رنج‌های IPv4 کلودفلر
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

CF_NETWORKS = [ipaddress.ip_network(net) for net in CF_RANGES]


def is_cf_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return any(ip_obj in net for net in CF_NETWORKS)
    except:
        return False


def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return None


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
        except:
            print(f"Failed: {src}")

    return list(all_configs)


def main():
    configs = fetch_sources()

    print(f"\nTotal unique configs: {len(configs)}\n")

    cf_ip_list = []
    workers_list = []
    cf_domain_list = []

    for conf in configs:

        if "://" not in conf:
            continue

        try:
            parsed = urlparse(conf)
            host = parsed.hostname
        except:
            continue

        if not host:
            continue

        # اگر IP مستقیم باشه
        try:
            ipaddress.ip_address(host)
            if is_cf_ip(host):
                cf_ip_list.append(conf)
            continue
        except:
            pass

        # اگر workers.dev باشه
        if host.endswith("workers.dev"):
            workers_list.append(conf)
            continue

        # دامنه عادی → resolve کنیم
        ip = resolve_domain(host)
        if ip and is_cf_ip(ip):
            cf_domain_list.append(conf)

    # ذخیره خروجی‌ها
    with open("cf_ip.txt", "w") as f:
        for c in cf_ip_list:
            f.write(c + "\n")

    with open("workers.txt", "w") as f:
        for c in workers_list:
            f.write(c + "\n")

    with open("cf_domain.txt", "w") as f:
        for c in cf_domain_list:
            f.write(c + "\n")

    print("Saved:")
    print(f"  Cloudflare IP configs: {len(cf_ip_list)}")
    print(f"  Workers configs: {len(workers_list)}")
    print(f"  CF-resolved domains: {len(cf_domain_list)}")


if __name__ == "__main__":
    main()
