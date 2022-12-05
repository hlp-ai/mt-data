"""0. Get WET file list from CommonCrawl"""
import argparse

from yimt_bitext.cc import get_wet_paths

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cc_id", type=str, default="CC-MAIN-2022-40", help="CommonCrawl archive ID")
    args = argparser.parse_args()

    wp = get_wet_paths(args.cc_id)
    print("# of WET file: ", len(wp))
