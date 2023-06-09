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
            if "moses/" in au :
                urls.append(au)
    return urls


if __name__ == "__main__":
    path = sys.argv[1]
    moses_links = get_moses_links(path)
    print(len(moses_links))
    for l in moses_links:
        print(l)


