"""解压一个目录下的ZIP文件"""
import argparse
import os
import zipfile

from yimt_bitext.utils.log import get_logger


def extract_zips(zips_dir, out_dir=None, logger_opus=None):
    """Unzip zip files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    if os.path.exists(out_dir):
        logger_opus.info("{} exits".format(out_dir))
        return out_dir

    zips = os.listdir(zips_dir)
    for zipf in zips:
        if not zipf.endswith(".zip"):
            continue

        if logger_opus:
            logger_opus.info("Unzip {}".format(zipf))

        zFile = zipfile.ZipFile(os.path.join(zips_dir, zipf), "r")
        for fileM in zFile.namelist():
            if fileM.rfind(".") == len(fileM)-3 or fileM.rfind(".") == len(fileM)-6:
                zFile.extract(fileM, out_dir)
        zFile.close()

    return out_dir


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--in_dir", type=str, required=True, help="zip file dir")
    argparser.add_argument("--out_dir", type=str, default=None, help="output dir")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "corpus")

    extract_zips(args.in_dir, args.out_dir, logger_opus=logger)
