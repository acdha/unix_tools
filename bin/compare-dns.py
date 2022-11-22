#!/usr/bin/env python3
"""Compare DNS records across multiple servers

Usage:

    compare-dns.py --server=ns1.example.com example.org:SOA example.org

You must specify at least one server and one record to check.
The query type is assume to be A if it does not end with a colon-separated
record type
"""

import optparse
import socket
import sys
from collections import defaultdict

from dns import resolver
from dns.resolver import NoAnswer

RDTYPE_SORT_WEIGHT = {"SOA": -3, "NS": -2, "MX": -1}


def get_records_from_server(server, records):
    r = resolver.Resolver()
    r.nameservers = [socket.gethostbyname(server)]
    r.search = []

    for qname, rdtype in records:
        try:
            for answer in r.query(qname, rdtype=rdtype):
                yield qname, rdtype, answer.to_text()
        except NoAnswer:
            yield qname, rdtype, None


def normalize_record(i):
    if ":" in i:
        return i.split(":", 1)
    else:
        return i, "A"


def query_sort_key(qname, rdtype):
    """Sort DNS responses by record type & name"""
    return RDTYPE_SORT_WEIGHT.get(rdtype, rdtype), qname


def main():
    parser = optparse.OptionParser(__doc__.strip())
    parser.add_option(
        "--server",
        type="str",
        dest="servers",
        action="append",
        metavar="SERVER",
        help="hostname of the DNS server to check (repeatable)",
    )

    (options, records) = parser.parse_args()

    if not records or not options.servers:
        parser.print_usage()
        sys.exit()

    records = map(normalize_record, records)

    results = defaultdict(lambda: defaultdict(list))

    for server in options.servers:
        print("Querying %s" % server)
        for qname, rdtype, resp in get_records_from_server(server, records):
            results[qname, rdtype][server].append(resp)
    print()

    for query, responses in sorted(
        results.items(), key=lambda i: query_sort_key(*i[0])
    ):
        print("%s:%s" % query)
        for server, answers in sorted(responses.items(), key=lambda i: i[0]):
            print("\t%s:" % server)
            for answer in sorted(answers):
                print("\t\t\t\t%s" % answer)
        print()


if __name__ == "__main__":
    main()
