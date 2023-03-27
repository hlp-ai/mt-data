import argparse
import json


def get_hosts(domains_fn, domain2host_fn):
    with open(domain2host_fn, encoding="utf-8") as f:
        domain2host = json.load(f)

    with open(domains_fn, encoding="utf-8") as f, open("hosts-to-crawl.txt", "w", encoding="utf-8") as out:
        for domain in f:
            domain = domain.strip()
            if domain in domain2host:
                for host in domain2host[domain]:
                    out.write(host + "\n")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--domains", type=str, required=True, help="domain list file")
    argparser.add_argument("--domain2host", type=str, required=True, help="domain-to-host file")
    args = argparser.parse_args()

    get_hosts(args.domains, args.domain2host)
