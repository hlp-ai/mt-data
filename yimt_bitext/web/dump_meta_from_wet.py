import argparse

from yimt_bitext.web.cc import dump_metadata_wet

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_path", type=str, required=True, help="WET file")
    argparser.add_argument("--output", type=str, default=None, help="Output metadata file")
    args = argparser.parse_args()

    dump_metadata_wet(args.wet_path, args.output)
