import requests
from urllib.parse import urlparse, parse_qs

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


def is_valid(config):
    if not config.startswith("vless://"):
        return False

    try:
        parsed = urlparse(config)
        query = parse_qs(parsed.query)

        security = query.get("security", [""])[0]
        sni = query.get("sni", [""])[0]

        if security != "tls":
            return False

        if not sni:
            return False

        return True

    except:
        return False


def main():
    configs = fetch_sources()
    print(f"\nTotal unique configs: {len(configs)}\n")

    valid = []

    for conf in configs:
        if is_valid(conf):
            valid.append(conf)

    with open("filtered.txt", "w") as f:
        for conf in valid:
            print(conf)
            f.write(conf + "\n")

    print(f"\nSaved {len(valid)} configs to filtered.txt")


if __name__ == "__main__":
    main()
