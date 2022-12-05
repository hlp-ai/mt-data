import gzip
import time

import requests

# cc_archive_id = "CC-MAIN-2022-40"
cc_base_url = "https://data.commoncrawl.org/"
cc_data_url = "https://data.commoncrawl.org/crawl-data/"
cc_wet_paths_gz = "wet.paths.gz"
cc_wet_paths = "wet.paths"


def download(url, local_fn):
    print("Downloading ", url)
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
    response = requests.request('GET', url, headers=hd)
    open(local_fn, 'wb').write(response.content)


def ungzip(zip_fn, unzip_fn):
    print("Unziping ", zip_fn)
    g = gzip.GzipFile(mode="rb", fileobj=open(zip_fn, 'rb'))
    open(unzip_fn, "wb").write(g.read())


def get_wet_paths(cc_archive_id):
    wet_paths_url = cc_data_url + cc_archive_id + "/" + cc_wet_paths_gz
    download(wet_paths_url, cc_wet_paths_gz)

    ungzip(cc_wet_paths_gz, cc_wet_paths)

    wetf = open(cc_wet_paths, encoding="utf-8")
    wet_paths = [cc_base_url+line.strip() for line in wetf]

    return wet_paths


wp = get_wet_paths("CC-MAIN-2022-40")
for p in wp:
    print(p)

start = time.time()
download(wp[4], "4.gz")
print(time.time() - start)
