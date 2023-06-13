import os
import sys

import requests

from yimt_bitext.opus.utils import logger_opus

OPUS_DOWNLOAD_BASE_URL = "https://object.pouta.csc.fi"


def download_opus_moses(corpus_name, corpus_version, sl, tl, out_dir="./"):
    format = "moses"
    corpus_path = "OPUS-" + corpus_name + "/" + corpus_version
    local_moses_file = os.path.join(out_dir, corpus_name + "-" + corpus_version + "-" + sl + "-" + tl + ".txt.zip")
    if os.path.exists(local_moses_file):
        logger_opus.info("{} exists".format(local_moses_file))
        return True
    remote_moses_file = sl + "-" + tl + ".txt.zip"
    moses_url = OPUS_DOWNLOAD_BASE_URL + "/" + corpus_path + "/" + format + "/" + remote_moses_file
    logger_opus.info(moses_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
    BLOCK_SIZE = 1024 * 1024
    total = 0

    try:
        r = requests.get(moses_url, headers=headers, timeout=(20, 20), stream=True, allow_redirects=False)
        if r.status_code != 200:
            logger_opus.info("{}: {}".format(moses_url, r.status_code))
            return False

        if 'content-length' in r.headers:
            content_size = int(r.headers['content-length'])
            logger_opus.info("{}: {:.4f} MB".format(moses_url, content_size/(1024*1024)))

        with open(local_moses_file, "wb") as f:
            for block in r.iter_content(BLOCK_SIZE):
                f.write(block)
                total += len(block)
                logger_opus.info("{}: {:.4f} MB".format(moses_url, total/(1024*1024)))
        return True
    except Exception as e:
        logger_opus.info("{}: {}".format(moses_url, e))
    finally:
        r.close()

    return False


# corpus_name = "KDE4"
# corpus_version = "v2"
# sl = "en"
# tl = "tr"
#
# success = download_opus_moses(corpus_name, corpus_version, sl, tl)
# print(success)


if __name__ == "__main__":
    corpora_list = sys.argv[1]
    langs_list = sys.argv[2]
    out_dir = sys.argv[3]

    to_zh = True

    langs = []
    with open(langs_list, encoding="utf-8") as f:
        for line in f:
            langs.append(line.strip())

    with open(corpora_list, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            corpus_name = parts[0]
            corpus_version = parts[1]

            for lang in langs:
                if to_zh:
                    tl = "zh"
                else:
                    tl = "en"

                sl = lang
                p = os.path.join(out_dir, sl + "-" + tl)
                os.makedirs(p, exist_ok=True)

                success = download_opus_moses(corpus_name, corpus_version, sl, tl, p)
                logger_opus.info(corpus_name + " " + sl + "-" + tl + " " + str(success))

                t = sl
                sl = tl
                tl = t
                success = download_opus_moses(corpus_name, corpus_version, sl, tl, p)
                logger_opus.info(corpus_name + " " + sl + "-" + tl + " " + str(success))
