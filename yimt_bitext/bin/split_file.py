"""将一个大文件平分成固定大小的多个文件"""
import argparse

from yimt_bitext.opus.utils import split
from yimt_bitext.utils.log import get_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument("--num", type=int, default=500000, help="the number of samples in each file")
    args = parser.parse_args()

    input = args.input
    sample_num = args.num

    logger = get_logger("./log.txt", "corpus")

    split(input, num_per_file=sample_num, logger=logger)
