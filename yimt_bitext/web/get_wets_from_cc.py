"""0. Get WET file list from CommonCrawl"""
import argparse

from yimt_bitext.web.cc import get_wet_paths

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cc_id", type=str, default="CC-MAIN-2022-40", help="CommonCrawl archive ID")
    argparser.add_argument("--out_dir", type=str, default=None, help="Output directory")
    args = argparser.parse_args()

    wp = get_wet_paths(args.cc_id, args.out_dir)
    print("# of WET file: ", len(wp))
