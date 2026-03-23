#!/usr/bin/env python3
"""
Search for an IP address in the published AWS IP ranges
"""

import argparse
import ipaddress
import json
from pathlib import Path
from time import time
from urllib.request import urlopen


def load_ip_ranges():
    ip_ranges_cache = Path("~/.local/state/aws/ip-ranges.json").expanduser()

    if not ip_ranges_cache.exists() or ip_ranges_cache.stat().st_mtime < (
        time() - 86400
    ):
        print(f"Saving the latest AWS IP ranges to {ip_ranges_cache}")
        ip_ranges_cache.parent.mkdir(exist_ok=True, parents=True)
        with urlopen("https://ip-ranges.amazonaws.com/ip-ranges.json") as source:
            with ip_ranges_cache.open("wb") as dest:
                dest.write(source.read())
    with ip_ranges_cache.open() as f:
        return json.load(f)


def search_ip_ranges(ip_ranges, target_addresses: list[ipaddress.IPv4Address]):
    for prefix_data in ip_ranges["prefixes"]:
        network = ipaddress.IPv4Network(prefix_data["ip_prefix"])

        for target_address in target_addresses:
            if target_address in network:
                yield target_address, prefix_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__.strip(),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(metavar="IP_ADDRESS", dest="ip_addresses", nargs="+")

    args = parser.parse_args()

    ip_ranges = load_ip_ranges()

    target_addresses = [ipaddress.IPv4Address(i) for i in args.ip_addresses]

    for ip_address, network_info in search_ip_ranges(ip_ranges, target_addresses):
        print(ip_address, network_info)
