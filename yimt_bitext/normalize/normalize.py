"""文件文本规范化"""
import argparse
import os

from yimt_bitext.utils.log import get_logger
from yimt_bitext.normalize.normalizers import load_normalizers


def normalize_file(in_path, normalizers, out_path=None, clean_after_done=False, logger=None):
    if logger:
        logger.info(normalizers)

    if out_path is None:
        out_path = in_path + ".normalized"

    if os.path.exists(out_path):
        logger.info("{} exists".format(out_path))
        return out_path

    n = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            for normalizer in normalizers:
                line = normalizer.normalize(line)

            if len(line) > 0:
                out_f.write(line + "\n")

            n += 1

            if n % 100000 == 0:
                if logger:
                    logger.info("Normalizing {}".format(n))
    if logger:
        logger.info("Normalizing {}".format(n))

    if clean_after_done:
        os.remove(in_path)

    return out_path


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", required=True, help="Input file path")
    argparser.add_argument("-o", "--output", default=None, help="Ouput file path")
    argparser.add_argument("-c", "--config", required=True, help="Normalizer config file")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "Normalize")

    logger.info("Loading normalizer config file: {}".format(args.config))
    normalizers = load_normalizers(args.config)

    normalize_file(args.input, normalizers, out_path=args.output, logger=logger)
