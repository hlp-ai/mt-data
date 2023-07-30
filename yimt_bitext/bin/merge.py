import argparse
import os

from yimt_bitext.opus.utils import merge
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True, help="input files or directories")
    parser.add_argument("-o", "--output", required=True, help="output file")
    parser.add_argument("--log_dir", default="./", help="log directory")
    args = parser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    merge(args.input, args.output, logger_opus=logger_opus)
