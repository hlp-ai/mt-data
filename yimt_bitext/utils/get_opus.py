import requests

OPUS_DOWNLOAD_BASE_URL = "https://object.pouta.csc.fi"
format = "moses"
corpus_name = "KDE4"
corpus_version = "v2"
sl = "en"
tl = "tr"

corpus_path = "OPUS-" + corpus_name + "/" + corpus_version
moses_file = sl + "-" + tl + ".txt.zip"
moses_url = OPUS_DOWNLOAD_BASE_URL + "/" +corpus_path + "/" + format + "/" + moses_file
print(moses_url)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
BLOCK_SIZE = 1024 * 64

try:
    r = requests.get(moses_url,  headers=headers, timeout=(15, 15), stream=True)
    with open(moses_file, "wb") as f:
        for block in r.iter_content(BLOCK_SIZE):
            f.write(block)
            print(".", end="")
except Exception as e:
    print(e)
finally:
    r.close()
