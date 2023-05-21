import gzip
import time

import requests

cc_base_url = "https://data.commoncrawl.org/"
cc_data_url = "https://data.commoncrawl.org/crawl-data/"
cc_wet_paths_gz = "wet.paths.gz"
cc_wet_paths = "wet.paths"
cc_wet_paths_done = cc_wet_paths + ".done"


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
        else:
            print("Error:", url, ":", response.status_code)
            return False
        end = time.time()
        print('Done！Time: %.2f secs' % (end - start))

        return True
    except Exception as e:
        print(e)
        return False
    finally:
        response.close()


def ungzip(zip_fn, unzip_fn):
    g = gzip.GzipFile(mode="rb", fileobj=open(zip_fn, 'rb'))
    with open(unzip_fn, "wb") as f:
        f.write(g.read())


def get_wet_name(wet_url):
    parts = wet_url.split("/")
    gz_path = parts[-1]
    idx = gz_path.find(".gz")
    return gz_path, gz_path[:idx]


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
