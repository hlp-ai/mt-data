"""0. Get WET file list from CommonCrawl"""
import argparse
import os

from yimt_bitext.web.cc import cc_data_url, cc_wet_paths_gz, download, cc_wet_paths, ungzip, cc_base_url


def get_wet_paths(cc_archive_id, out_dir=None):
    """Download, unzip and get WET file urls"""
    wet_paths_url = cc_data_url + cc_archive_id + "/" + cc_wet_paths_gz
    if out_dir is None:
        out_dir = "./" + cc_archive_id + "/"
    if not os.path.exists(out_dir):
        print("Making directory ", out_dir)
        os.makedirs(out_dir, exist_ok=True)

    # download
    cc_wet_paths_gz_path = os.path.join(out_dir, cc_wet_paths_gz)
    download(wet_paths_url, cc_wet_paths_gz_path)

    # unzip
    cc_wet_paths_path = os.path.join(out_dir, cc_wet_paths)
    ungzip(cc_wet_paths_gz_path, cc_wet_paths_path)

    # read WET files
    wetf = open(cc_wet_paths_path, encoding="utf-8")
    wet_paths = [cc_base_url+line.strip() for line in wetf]

    return wet_paths


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cc_id", type=str, default="CC-MAIN-2022-40", help="CommonCrawl archive ID")
    argparser.add_argument("--out_dir", type=str, default=None, help="Output directory")
    args = argparser.parse_args()

    wp = get_wet_paths(args.cc_id, args.out_dir)
    print("# of WET file: ", len(wp))
