import os
import zipfile


from yimt_bitext.utils.log import get_logger


logger_opus = get_logger("opus.log", "mt.opus")


def extract_zips(zips_dir, out_dir=None):
    """Unzip zip files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    zips = os.listdir(zips_dir)
    for zipf in zips:
        if not zipf.endswith(".zip"):
            continue

        logger_opus.info("Unzip {}".format(zipf))

        zFile = zipfile.ZipFile(os.path.join(zips_dir, zipf), "r")
        for fileM in zFile.namelist():
            if fileM.rfind(".") == len(fileM)-3 or fileM.rfind(".") == len(fileM)-6:
                zFile.extract(fileM, out_dir)
        zFile.close()

    return out_dir