import argparse
import os
import zipfile

from yimt_bitext.utils.log import get_logger


def test_zip_file(zf):
    zFile = None
    try:
        zFile = zipfile.ZipFile(zf)
        for fileM in zFile.namelist():
            pass

        return True
        # ret = the_zip_file.testzip()
        #
        # if ret is not None:
        #     return False
        # else:
        #     return True
    except Exception as e:
        return False
    finally:
        if zFile is not None:
            zFile.close()


def check_zip_dir(d, logger):
    zips = os.listdir(d)
    for zipf in zips:
        if not zipf.endswith(".zip"):
            continue
        full_zip_f = os.path.join(d, zipf)
        logger.info("Checking {}".format(full_zip_f))
        if not test_zip_file(full_zip_f):
            logger.warning("{} is bad! Delete it.".format(full_zip_f))
            os.remove(full_zip_f)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", type=str, required=True, help="zip file dir")
    argparser.add_argument("-r", "--recursive", action="store_true", help="对子目录检查")
    args = argparser.parse_args()

    logger = get_logger("./log.txt", "OPUS")

    if not args.recursive:
        check_zip_dir(os.path.join(args.input), logger)
    else:
        zips = os.listdir(args.input)
        for d in zips:
            check_zip_dir(os.path.join(args.input, d), logger)