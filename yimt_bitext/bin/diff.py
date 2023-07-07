import argparse

from yimt_bitext.opus.utils import diff_tsv
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C1-C2")
    parser.add_argument("-i1", "--input1", required=True, help="input file1")
    parser.add_argument("-i2", "--input2", required=True, help="input file2")
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    diff_tsv(args.input1, args.input2, args.output, creterion="SRC", logger=logger)
