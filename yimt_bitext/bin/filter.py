import argparse

from yimt_bitext.utils.filters import filter_file, load_filters
from yimt_bitext.utils.log import get_logger


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--output", default=None, help="Ouput file path")
    argparser.add_argument("--config", required=True, help="Filter config file")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    filters = load_filters(args.config)

    filter_file(args.input, filters=filters, out_path=args.output, logger=logger)
