"""1. Download, parse WET files from CommonCrawl and dump metadata for each WET file"""
import argparse
import os

from warcio import ArchiveIterator

from yimt_bitext.web.cc import get_wet_name, download_progress, ungzip, cc_base_url, cc_wet_paths, \
    cc_wet_paths_done
from yimt_bitext.web.web import URL


def iter_metadata_wet(wet_path):
    """Iterate WET record"""
    with open(wet_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'conversion':
                # TODO: When WARC-Identified-Content-Language is not available, language identification is needed.
                langs = record.rec_headers.get_header("WARC-Identified-Content-Language")
                url = record.rec_headers.get_header("WARC-Target-URI")
                content_len = int(record.rec_headers.get_header("Content-Length"))
                if langs is not None:
                    langs = langs.split(",")
                else:
                    langs = []

                u = URL(url)
                site = u.scheme + "://" + u.netloc + "/"
                domain = u.fld

                # TODO: More precise lengths of text of different languages
                if len(langs) > 0:
                    most_prob_lang = langs[0]
                    yield url, site, domain, most_prob_lang, content_len


def dump_metadata_wet(wet_path, out_fn=None):
    if out_fn is None:
        out_fn = os.path.join(os.path.dirname(wet_path), os.path.basename(wet_path) + ".meta")

    report_interval = 10000
    total = 0
    with open(out_fn, "w", encoding="utf-8") as stream:
        for url, site, domain, lang, content_len in iter_metadata_wet(wet_path):
            print(url, site, domain, lang, content_len, file=stream)
            total += 1
            if total % report_interval == 0:
                print(total)
    print(total)


def dump_wet(wet_paths, wet_urls_processed_path):
    # read processed WET file list
    wet_urls_processed = set()
    if os.path.exists(wet_urls_processed_path):
        with open(wet_urls_processed_path, encoding="utf-8") as f:
            for u in f:
                wet_urls_processed.add(u.strip())

    print("# of WET processed: ", len(wet_urls_processed))

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            if wet_url in wet_urls_processed:  # skip processed WET file
                print(wet_url, " has been processed before")
                continue

            print("Dump metadata for ", wet_url)
            wet_gz_name, wet_name = get_wet_name(wet_url)

            wet_gz_path = os.path.join(args.wet_paths_dir, wet_gz_name)
            wet_path = os.path.join(args.wet_paths_dir, wet_name)

            # download WET file
            download_progress(wet_url, wet_gz_path)

            # unzip WET file
            ungzip(wet_gz_path, wet_path)

            # Parse and dump wet metadata
            print("Scanning ", wet_path)
            dump_metadata_wet(wet_path)

            print("Updating WET done file...")
            with open(wet_urls_processed_path, "a", encoding="utf-8") as f:
                f.write(wet_url + "\n")

            print("Deleting downloaded file")
            os.remove(wet_gz_path)
            os.remove(wet_path)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_paths_dir", required=True, help="Directory of wet.paths file")
    args = argparser.parse_args()

    wet_paths = os.path.join(args.wet_paths_dir, cc_wet_paths)
    wet_urls_processed_path = os.path.join(args.wet_paths_dir, cc_wet_paths_done)

    dump_wet(wet_paths, wet_urls_processed_path)
