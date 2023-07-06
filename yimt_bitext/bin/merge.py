import argparse

from yimt_bitext.opus.utils import merge
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True, help="input files or directories")
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    merge(args.input, args.output, logger_opus=logger)
