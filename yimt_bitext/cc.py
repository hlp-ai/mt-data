import gzip
import os
import time
from urllib.parse import urlparse

import requests

# cc_archive_id = "CC-MAIN-2022-40"
from warcio import ArchiveIterator

cc_base_url = "https://data.commoncrawl.org/"
cc_data_url = "https://data.commoncrawl.org/crawl-data/"
cc_wet_paths_gz = "wet.paths.gz"
cc_wet_paths = "wet.paths"
cc_wet_paths_done = cc_wet_paths + ".done"
cc_stat_host_file = "stat_host.json"


def download(url, local_fn):
    print("Downloading ", url)
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
    response = requests.request('GET', url, headers=hd)
    open(local_fn, 'wb').write(response.content)


def download_progress(url, filepath):
    start = time.time()
    response = requests.get(url, stream=True)
    size = 0
    chunk_size = 4096 * 16
    content_size = int(response.headers['content-length'])
    try:
        if response.status_code == 200:
            print('Start downloading,[File Size]:{size:.2f} MB'.format(size=content_size / 1024 / 1024))
            with open(filepath, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    print('\r' + '[Progress]:%s%.2f%%' % (
                        '>' * int(size * 50 / content_size), float(size / content_size * 100)), end=' ')
        end = time.time()
        print('Done！Time: %.2f secs' % (end - start))
    except Exception:
        pass


def ungzip(zip_fn, unzip_fn):
    print("Unziping ", zip_fn, " into ", unzip_fn)
    g = gzip.GzipFile(mode="rb", fileobj=open(zip_fn, 'rb'))
    open(unzip_fn, "wb").write(g.read())


def get_wet_paths(cc_archive_id, out_dir=None):
    wet_paths_url = cc_data_url + cc_archive_id + "/" + cc_wet_paths_gz
    if out_dir is None:
        out_dir = "./" + cc_archive_id + "/"
    if not os.path.exists(out_dir):
        print("Making directory ", out_dir)
        os.makedirs(out_dir, exist_ok=True)
    cc_wet_paths_gz_path = os.path.join(out_dir, cc_wet_paths_gz)
    download(wet_paths_url, cc_wet_paths_gz_path)

    cc_wet_paths_path = os.path.join(out_dir, cc_wet_paths)
    ungzip(cc_wet_paths_gz_path, cc_wet_paths_path)

    wetf = open(cc_wet_paths_path, encoding="utf-8")
    wet_paths = [cc_base_url+line.strip() for line in wetf]

    return wet_paths


def get_wet_name(wet_url):
    parts = wet_url.split("/")
    gz_path = parts[-1]
    idx = gz_path.find(".gz")
    return gz_path, gz_path[:idx]


def count_lang(wet_path, host2lang2len, urls_file=None):
    new_hosts = 0
    if urls_file is not None:
        urlf = open(urls_file, "a", encoding="utf-8")
    else:
        urlf = None

    with open(wet_path, 'rb') as stream:
        i = 0
        for record in ArchiveIterator(stream):
            if record.rec_type == 'conversion':
                # TODO: When WARC-Identified-Content-Language is not available, language identification is needed.
                langs = record.rec_headers.get_header("WARC-Identified-Content-Language")
                url = record.rec_headers.get_header("WARC-Target-URI")
                content_len = int(record.rec_headers.get_header("Content-Length"))
                if langs is not None:
                    langs = langs.split(",")
                else:
                    langs = []

                if urlf is not None:
                    urlf.write(url + "\n")

                u = urlparse(url)
                host = u.scheme + "://" + u.netloc + "/"
                # host = get_domain(u)

                if host not in host2lang2len:
                    host2lang2len[host] = {}
                    new_hosts += 1

                lang2len = host2lang2len[host]

                for lang in langs:
                    if lang in lang2len:
                        lang2len[lang] += content_len
                    else:
                        lang2len[lang] = content_len

            i += 1

            if i % 2000 == 0:
                print(i, " URLs")

    print(i, " URLs")

    if urlf is not None:
        urlf.close()

    return new_hosts
