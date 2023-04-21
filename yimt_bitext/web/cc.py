import gzip
import time
from urllib.parse import urlparse

import requests

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
    if response.ok:
        open(local_fn, 'wb').write(response.content)
        return True
    else:
        return False


def download_progress(url, filepath):
    start = time.time()
    response = requests.get(url, stream=True)
    size = 0
    chunk_size = 4096 * 16
    if 'content-length' in response.headers:
        content_size = int(response.headers['content-length'])
    else:
        content_size = 1024*1024
    try:
        if response.status_code == 200:
            print('Start downloading, [File Size]: {size:.2f} MB'.format(size=content_size / 1024 / 1024))
            with open(filepath, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    print('\r' + '[Progress]: %s%.2f%%' % (
                        '>' * int(size * 50 / content_size), float(size / content_size * 100)), end=' ')
        end = time.time()
        print('Done！Time: %.2f secs' % (end - start))

        return True
    except Exception as e:
        print(e)
        return False


def ungzip(zip_fn, unzip_fn):
    print("Unziping ", zip_fn, " into ", unzip_fn)
    g = gzip.GzipFile(mode="rb", fileobj=open(zip_fn, 'rb'))
    with open(unzip_fn, "wb") as f:
        f.write(g.read())


def get_wet_name(wet_url):
    parts = wet_url.split("/")
    gz_path = parts[-1]
    idx = gz_path.find(".gz")
    return gz_path, gz_path[:idx]


def count_lang(wet_path, host2lang2len, urls_file=None):
    print("Scanning ", wet_path)
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

                # TODO: More precise lengths of text of different languages
                if len(langs) > 0:
                    most_prob_lang = langs[0]
                    if most_prob_lang in lang2len:
                        lang2len[most_prob_lang] += content_len
                    else:
                        lang2len[most_prob_lang] = content_len

                # for lang in langs:
                #     if lang in lang2len:
                #         lang2len[lang] += content_len
                #     else:
                #         lang2len[lang] = content_len

            i += 1

            if i % 2000 == 0:
                print(i, " URLs")

    print(i, " URLs")

    if urlf is not None:
        urlf.close()

    return new_hosts


# def stat_from_meta(meta_file):
#     host2lang2len = {}
#
#     report_interval = 20000
#     total = 0
#
#     with open(meta_file, encoding="utf-8") as f:
#         for line in f:
#             parts = line.strip().split()
#             url, host, domain, lang, content_len = parts
#             content_len = int(content_len)
#
#             update_k2dict(host2lang2len, host, lang, content_len)
#
#             total += 1
#             if total % report_interval == 0:
#                 print(" ", total, "urls")
#         print(" ", total, "urls")
#
#     return host2lang2len


def update_k2set(k2list, k, v):
    if k not in k2list:
        k2list[k] = []

    if v not in k2list[k]:
        k2list[k].append(v)


def merge_k2set(k2set1, k2set2):
    for k, s in k2set2.items():
        for ss in s:
            update_k2set(k2set1, k, ss)

    return k2set1


def update_k2dict(k2dict, k, kk, kv):
    if k not in k2dict:
        k2dict[k] = {}

    if kk in k2dict[k]:
        k2dict[k][kk] += kv
    else:
        k2dict[k][kk] = kv


def merge_k2dict(k2dict1, kd2dict2):
    for k, dic in kd2dict2.items():
        for kk, kv in dic.items():
            update_k2dict(k2dict1, k, kk, kv)

    return k2dict1


# if __name__ == "__main__":
#     wet_path = r"D:\dataset\text\cc22-40\CC-MAIN-20220924151538-20220924181538-00000.warc.wet"
#     # for url, site, domain, lang, content_len in iter_metadata_wet(wet_path):
#     #     print(url, site, domain, lang, content_len)
#
#     # dump_metadata_wet(wet_path)
#     s_by_host, s_by_domain = stat_from_meta(
#         r"./CC-MAIN-2022-40/CC-MAIN-20220924151538-20220924181538-00000.warc.wet.meta")
#     for domain, lang2len in s_by_domain.items():
#         if len(lang2len) > 1:
#             print(domain, lang2len)
