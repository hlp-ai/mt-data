"""文件文本规范化"""
import argparse

from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import normalize_file, load_normalizers

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--output", default=None, help="Ouput file path")
    argparser.add_argument("--config", required=True, help="Normalizer config file")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    logger.info("Loading normalizer config file: {}".format(args.config))
    normalizers = load_normalizers(args.config)

    normalize_file(args.input, normalizers, out_path=args.output, logger=logger)
