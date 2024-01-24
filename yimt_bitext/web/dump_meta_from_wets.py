"""1. Download, parse WET files from CommonCrawl and dump metadata for each WET file"""
import argparse
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from warcio import ArchiveIterator

from yimt_bitext.utils.lang import detect_lang
from yimt_bitext.utils.log import get_logger
from yimt_bitext.web.cc import get_wet_name, download_progress, ungzip, cc_base_url, cc_wet_paths, \
    cc_wet_paths_done
from yimt_bitext.web.web import URL


def iter_metadata_wet(wet_path):
    """Iterate WET record"""
    with open(wet_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'conversion' and record.rec_headers.get_header('Content-Type').find('text/')==0:
                langs = record.rec_headers.get_header("WARC-Identified-Content-Language")
                url = record.rec_headers.get_header("WARC-Target-URI")
                content_len = int(record.rec_headers.get_header("Content-Length"))
                if langs is not None:
                    langs = langs.split(",")
                else:
                    logger_wet.warning("NO WARC-Identified-Content-Language in WET for {}".format(url))
                    content = record.content_stream().read().decode("utf-8")
                    lang = detect_lang(content)
                    logger_wet.warning("{} detected: {}".format(url, lang))
                    langs = [lang]

                u = URL(url)
                site = u.scheme + "://" + u.netloc + "/"
                domain = u.fld

                # TODO: More precise lengths of text of different languages
                if len(langs) > 0:
                    most_prob_lang = langs[0]
                    yield url, site, domain, most_prob_lang, content_len


def dump_metadata_wet(wet_path, out_fn=None):
    if out_fn is None:
        out_fn = os.path.join(os.path.dirname(wet_path), os.path.basename(wet_path) + ".meta")

    total = 0
    with open(out_fn, "w", encoding="utf-8") as stream:
        for url, site, domain, lang, content_len in iter_metadata_wet(wet_path):
            print(url, site, domain, lang, content_len, file=stream)
            total += 1

    return total


logger_wet = get_logger(log_filename="./dump_wets.log", name="WET")


def download_wet(url, filepath):
    start = time.time()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    response = requests.get(url, header, stream=True)
    size = 0
    chunk_size = 4096 * 16
    n_read = 0

    try:
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    n_read += 1
                    if n_read % 64 == 0:
                        logger_wet.info("{}: {:.2f}M {:.1f} secs".format(url, size/(1024*1024), (time.time()-start)))
        else:
            logger_wet.warning("Error: {}: {}".format(url, response.status_code))
            return False
        logger_wet.info("{} Downloaded: {:.2f}M {:.1f} secs".format(url, size/(1024*1024), (time.time()-start)))

        return True
    except Exception as e:
        logger_wet.warning(e)
        return False
    finally:
        response.close()


def process_wet_url(wet_url):
    logger_wet.info("Dump metadata for {}".format(wet_url))
    wet_gz_name, wet_name = get_wet_name(wet_url)

    wet_gz_path = os.path.join(args.wet_paths_dir, wet_gz_name)
    wet_path = os.path.join(args.wet_paths_dir, wet_name)

    # download WET file
    if not download_wet(wet_url, wet_gz_path):
        return False, wet_url

    # unzip WET file
    logger_wet.info("Unziping {} into {}".format(wet_gz_path, wet_path))
    ungzip(wet_gz_path, wet_path)

    # Parse and dump wet metadata
    logger_wet.info("Scanning {}".format(wet_path))
    n = dump_metadata_wet(wet_path)
    logger_wet.info("{} urls scanned.".format(n))

    logger_wet.info("Deleting downloaded file")
    os.remove(wet_gz_path)
    os.remove(wet_path)

    return True, wet_url


def dump_wet_batch(wet_paths, wet_urls_processed_path, max_workers = 4):
    # read processed WET file list
    wet_urls_processed = set()
    if os.path.exists(wet_urls_processed_path):
        with open(wet_urls_processed_path, encoding="utf-8") as f:
            for u in f:
                wet_urls_processed.add(u.strip())

    logger_wet.info("# of WET processed: {}".format(len(wet_urls_processed)))

    to_dump_wet_urls = []

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            if wet_url in wet_urls_processed:  # skip processed WET file
                logger_wet.info("{} has been processed before".format(wet_url))
                continue

            to_dump_wet_urls.append(wet_url)

    executor = ThreadPoolExecutor(max_workers=max_workers)
    for success, u in executor.map(process_wet_url, to_dump_wet_urls):
        if success:
            logger_wet.info("Finish {}".format(u))
            with open(wet_urls_processed_path, "a", encoding="utf-8") as f:
                f.write(u + "\n")


def dump_wet(wet_paths, wet_urls_processed_path):
    # read processed WET file list
    wet_urls_processed = set()
    if os.path.exists(wet_urls_processed_path):
        with open(wet_urls_processed_path, encoding="utf-8") as f:
            for u in f:
                wet_urls_processed.add(u.strip())

    logger_wet.info("# of WET processed: {}".format(len(wet_urls_processed)))

    with open(wet_paths, encoding="utf-8") as f:
        for wet_url in f:  # for each wet file in cc archive
            wet_url = cc_base_url + wet_url.strip()
            if wet_url in wet_urls_processed:  # skip processed WET file
                logger_wet.info("{} has been processed before".format(wet_url))
                continue

            logger_wet.info("Dump metadata for {}".format(wet_url))
            wet_gz_name, wet_name = get_wet_name(wet_url)

            wet_gz_path = os.path.join(args.wet_paths_dir, wet_gz_name)
            wet_path = os.path.join(args.wet_paths_dir, wet_name)

            # download WET file
            if not download_progress(wet_url, wet_gz_path):
                continue

            # unzip WET file
            ungzip(wet_gz_path, wet_path)

            # Parse and dump wet metadata
            logger_wet.info("Scanning {}".format(wet_path))
            dump_metadata_wet(wet_path)

            logger_wet.info("Updating WET done file...")
            with open(wet_urls_processed_path, "a", encoding="utf-8") as f:
                f.write(wet_url + "\n")

            logger_wet.info("Deleting downloaded file")
            os.remove(wet_gz_path)
            os.remove(wet_path)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--wet_paths_dir", required=True, help="Directory of wet.paths file")
    argparser.add_argument("--max_workers", type=int, default=1, help="# of threads to download WET files")
    args = argparser.parse_args()

    wet_paths = os.path.join(args.wet_paths_dir, cc_wet_paths)
    wet_urls_processed_path = os.path.join(args.wet_paths_dir, cc_wet_paths_done)

    # dump_wet(wet_paths, wet_urls_processed_path)
    dump_wet_batch(wet_paths, wet_urls_processed_path, args.max_workers)
