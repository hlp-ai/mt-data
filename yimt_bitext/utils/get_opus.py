import os
import requests


OPUS_DOWNLOAD_BASE_URL = "https://object.pouta.csc.fi"


def download_opus_moses(corpus_name, corpus_version, sl, tl, out_dir="./"):
    format = "moses"
    corpus_path = "OPUS-" + corpus_name + "/" + corpus_version
    local_moses_file = os.path.join(out_dir, corpus_name + "-" + corpus_version + "-" + sl + "-" + tl + ".txt.zip")
    remote_moses_file = sl + "-" + tl + ".txt.zip"
    moses_url = OPUS_DOWNLOAD_BASE_URL + "/" + corpus_path + "/" + format + "/" + remote_moses_file
    print(moses_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
    BLOCK_SIZE = 1024 * 1024
    total = 0

    try:
        r = requests.get(moses_url, headers=headers, timeout=(15, 15), stream=True, allow_redirects=False)
        if r.status_code != 200:
            print(moses_url, r.status_code)
            return False

        if 'content-length' in r.headers:
            content_size = int(r.headers['content-length'])
            print("{}: {}".format(moses_url, content_size))

        with open(local_moses_file, "wb") as f:
            for block in r.iter_content(BLOCK_SIZE):
                f.write(block)
                total += len(block)
                print("{}: {}".format(moses_url, total))
        return True
    except Exception as e:
        print(moses_url, e)
    finally:
        r.close()


corpus_name = "KDE4"
corpus_version = "v2"
sl = "en"
tl = "tr"

success = download_opus_moses(corpus_name, corpus_version, sl, tl)
print(success)
