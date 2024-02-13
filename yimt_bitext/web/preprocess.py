"""5. 对单语文本文件进行清理和去重，可选分句"""
import argparse
import os

from yimt_bitext.dedup.dedup import dedup_file
from yimt_bitext.split.text_splitter import split_sent_file
from yimt_bitext.utils.clean import clean_file
from yimt_bitext.utils.log import get_logger


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dir", required=True, help="Directory for crawled domain")
    argparser.add_argument("--split", action="store_true", help="split text into sentences or not")
    args = argparser.parse_args()

    domain_dir = args.dir
    sents_dir = os.path.join(domain_dir, "lang2sents")

    logger = get_logger(os.path.join(sents_dir, "preproccess.log"))

    for f in os.listdir(sents_dir):
        if not f.endswith(".txt"):
            continue
        lang = os.path.basename(f)
        f = os.path.join(sents_dir, f)
        logger.info("Cleaning {}...".format(f))
        out = clean_file(f, logger=logger)

        if args.split:
            logger.info("Splitting {}...".format(out))
            out = split_sent_file(out, lang=lang)

        logger.info("Deduping {}...".format(out))
        dedup_file(out, logger=logger, remove_noletter=False)
