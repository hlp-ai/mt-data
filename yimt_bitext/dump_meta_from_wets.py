"""1. Download, parse WET files from CommonCrawl and dump metadata for each WET file"""
import argparse
import os

from yimt_bitext.cc import get_wet_name, download_progress, ungzip, cc_base_url, cc_wet_paths, \
    cc_wet_paths_done, dump_metadata_wet

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_paths_dir", required=True, help="Directory of wet.paths file")
    args = argparser.parse_args()

    wet_paths = os.path.join(args.wet_paths_dir, cc_wet_paths)
    wet_urls_processed_path = os.path.join(args.wet_paths_dir, cc_wet_paths_done)

    wet_urls_processed = set()
    if os.path.exists(wet_urls_processed_path):
        with open(wet_urls_processed_path, encoding="utf-8") as f:
            for u in f:
                wet_urls_processed.add(u.strip())

    print("# of WET processed: ", len(wet_urls_processed))

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            if wet_url in wet_urls_processed:
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
