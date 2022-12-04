from urllib.parse import urlparse

from bs4 import BeautifulSoup

from html.parser import HTMLParser

from tld import get_fld
from tld.exceptions import TldDomainNotFound


def get_host(url):
    u = urlparse(url)
    host = u.netloc
    return host


def get_domain(url):
    try:
        return get_fld(url)
    except TldDomainNotFound:
        return get_host(url)


class PageCollector(HTMLParser):
    """Collect paragraphs from html page"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.doc = []
        self.p = []
        self.in_doc = False

    def handle_starttag(self, tag, attrs):
        # print('<%s>' % tag)
        if tag == "body":
            self.in_doc = True
        elif tag == "script" or tag == "style" or tag == "title":
            self.in_doc = False
        else:
            self.in_doc = True

        if tag == "br":
            self.doc.append("".join(self.p))
            self.p = []

    def handle_endtag(self, tag):
        # print('</%s>' % tag)
        if tag == "script" or tag == "style" or tag == "title":
            self.in_doc = True

        if (tag == "p" or tag == "div" or tag == "span"
                or tag == "h3" or tag == "h2" or tag == "h1"
                or tag == "ul" or tag == "li" or tag == "tr"):
            self.doc.append("".join(self.p))
            self.p = []

    def handle_startendtag(self, tag, attrs):
        # print('<%s/>' % tag)
        if tag == "br":
            self.doc.append("".join(self.p))
            self.p = []

    def handle_data(self, data):
        if self.in_doc:
            self.p.append(data)


def get_text(html_txt):
    parser = PageCollector()
    parser.feed(html_txt)
    parser.close()

    return "\n".join(parser.doc)


def get_text_bs4(html_txt):
    soup = BeautifulSoup(html_txt, 'html.parser')
    return soup.body.get_text()


if __name__ == "__main__":
    u1 = "http://www.baidu.com"
    print(get_domain(u1))

    u1 = "http://www.baidu.com:8888/"
    print(get_domain(u1))

    u1 = "http://www.hust.edu.cn"
    print(get_domain(u1))

    u1 = "http://sse.hust.edu.cn"
    print(get_domain(u1))

    u1 = "https://192.168.1.1:5555"
    print(get_domain(u1))

