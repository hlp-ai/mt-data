"""从OPUS语言对平行语料列表网页中抽取语料文件URL"""
import sys

from bs4 import BeautifulSoup


def get_moses_links(html_file):
    page = open(html_file, encoding="utf-8").read()

    d = BeautifulSoup(page, "lxml")
    aa = d.find_all("a")
    urls = []
    for a in aa:
        if a.has_attr("href"):
            au = a["href"]
            if "moses/" in au :  # TODO: OPUS网页布局已改变，这个模式匹配有问题
                urls.append(au)
    return urls


if __name__ == "__main__":
    path = sys.argv[1]
    moses_links = get_moses_links(path)
    print(len(moses_links))
    for l in moses_links:
        print(l)
