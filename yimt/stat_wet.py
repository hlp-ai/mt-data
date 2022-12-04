"""1. Count the total lengths of text with different languages for hosts from WET file of CommonCrawl"""
import argparse
import json
import os

from warcio.archiveiterator import ArchiveIterator
from urllib.parse import urlparse

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_path", type=str, required=True, help="WET file")
    argparser.add_argument("--stat_path", type=str, default="./stat_host.json", help="stat file")
    args = argparser.parse_args()

    wet_path = args.wet_path # r"D:\dataset\text\cc22-40\CC-MAIN-20220924151538-20220924181538-00001.warc.wet"
    stat_path = args.stat_path

    host2lang2len = {}

    if os.path.exists(stat_path):
        with open(stat_path, encoding="utf-8") as f:
            print("Loading stat file for updating...")
            host2lang2len = json.load(f)

    print("# hosts: ", len(host2lang2len))

    new_hosts = 0

    with open(wet_path, 'rb') as stream:
        i = 0
        for record in ArchiveIterator(stream):
            if record.rec_type == 'conversion':
                langs = record.rec_headers.get_header("WARC-Identified-Content-Language")
                url = record.rec_headers.get_header("WARC-Target-URI")
                content_len = int(record.rec_headers.get_header("Content-Length"))
                if langs is not None:
                    langs = langs.split(",")
                else:
                    langs = []

                u = urlparse(url)
                host = u.netloc

                if host not in host2lang2len:
                    host2lang2len[host] = {}
                    new_hosts += 1

                lang2len = host2lang2len[host]

                for lang in langs:
                    if lang in lang2len:
                        lang2len[lang] += content_len
                    else:
                        lang2len[lang] = content_len

                # print(host, url, langs, content_len)
                # print(record.rec_headers.get_header("WARC-Identified-Content-Language"),
                #       record.rec_headers.get_header("WARC-Target-URI"),
                #       record.rec_headers.get_header("Content-Length"))
                # print(record.content_stream().read().decode("utf-8"))
                # print()
            i += 1
            # if i >= 10000:
            #     break

            if i % 10000 == 0:
                print(i)
            # if record.rec_type == 'response':
            #     print(record.rec_headers.get_header('WARC-Target-URI'))

    print("# new hosts: ", new_hosts)
    print("# hosts: ", len(host2lang2len))
    print("Writing stat file...")
    with open(stat_path, "w", encoding="utf-8") as stream:
        json.dump(host2lang2len, stream)

