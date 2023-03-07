#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from difflib import get_close_matches, SequenceMatcher
from collections import defaultdict
from languagestripper import LanguageStripper
from urllib.parse import urlparse


def read_urls(infile):
    urls=[]
    f = open(infile)
    for line in f.readlines():
        urls.append(line.strip())
    return urls

def n_longest(l, n=2, discounted=None):
    items = [[len(i), i] for i in l]

    if discounted:
        for j, i in enumerate(l):
            if i in discounted:
                items[j][0] -= 100

    items.sort(reverse=True)
    return [i for _, i in items[:n]]


def normalize_url(url):
    """ It seems some URLs have an empty query string.
    This function removes the trailing '?' """
    url = url.rstrip('?')
    if not url.startswith("http://"):
        url = ''.join(("http://", url))
    return url


def get_netloc(uri):
    parsed_uri = urlparse.urlparse(uri)
    netloc = parsed_uri.netloc
    if '@' in netloc:
        netloc = netloc.split('@')[1]
    if ':' in netloc:
        netloc = netloc.split(':')[0]
    return netloc


def strip_urls(urls, lang=None):
    stripped = defaultdict(set)
    language_stripper = LanguageStripper(languages=[lang])
    for url in urls:
        stripped_url, success = language_stripper.strip_uri(
            url, expected_language=lang)
        if success:
            # if stripped_url in stripped:
            #     print stripped_url, url, stripped[stripped_url]
            stripped[stripped_url].add(url)      #根据语言类决定是否加入
    return stripped


def find_pairs(source_urls, target_urls,
               source_stripped, target_stripped):
    pairs = []
    # stripped source url matches unstripped target url
    # e.g. mypage.net/index.html?lang=fr <-> mypage.net/index.html
    for stripped_source_url in set(
            source_stripped.keys()).intersection(target_urls):
        tu = stripped_source_url
        for su in source_stripped[stripped_source_url]:
            pairs.append((su, tu))
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d) \n"
        % (npairs, "stripped source + unmodified target",
           npairs))

    # stripped target url matches unstripped source url.
    # e.g. lesite.fr/en/bonsoir <-> lesite.fr/bonsoir
    for stripped_target_url in set(
            target_stripped.keys()).intersection(source_urls):
        su = stripped_target_url
        for tu in target_stripped[stripped_target_url]:
            pairs.append((su, tu))

    oldpairs = npairs
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d) \n"
        % (npairs - oldpairs, "stripped target + unmodified source",
           npairs))

    # stripped source url matches stripped target url
    # e.g. page.net/fr <-> page.net/en
    oldpairs = len(pairs)
    for stripped_source_url, source_url in source_stripped.items():
        if stripped_source_url in target_stripped:
            for su in source_url:
                for tu in target_stripped[stripped_source_url]:
                    pairs.append((su, tu))

    oldpairs = npairs
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d)\n"
        % (npairs - oldpairs, "stripped source + stripped target",
           npairs))

    return pairs


if __name__ == "__main__":
    source_urls = read_urls('source_urls.txt')
    target_urls = read_urls('target_urls.txt')
    source_stripped = strip_urls(source_urls, 'zh')
    target_stripped = strip_urls(target_urls, 'jp')
    print("%d/%d stripped source/target urls" % (len(source_stripped), len(target_stripped)))
    pairs = find_pairs(source_urls, target_urls, source_stripped, target_stripped)
    sys.stderr.write("Total: %d candidate pairs\n" % (len(set(pairs))))
    for pair in pairs:
        print(pair)
