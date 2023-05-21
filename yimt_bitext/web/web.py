from urllib.parse import urlparse

from bs4 import BeautifulSoup

from html.parser import HTMLParser

from tld import get_fld, get_tld


class URL:

    def __init__(self, url):
        self.origin_url = url
        u = urlparse(url)
        self.netloc = u.netloc
        self.scheme = u.scheme
        self.port = 80
        self.host = self.netloc
        idx = self.netloc.find(":")
        if idx >= 0:
            self.host = self.netloc[:idx]
            port_str = self.netloc[idx+1:]
            port_str = port_str.strip()
            if len(port_str) > 0 and port_str.isdecimal():
                self.port = int(port_str)
        self.path = u.path
        self.query = u.query
        self.params = u.params
        self.fragemnt = u.fragment
        try:
            self.fld = get_fld(url)
            self.tld = get_tld(url)
        except Exception:
            self.fld = self.netloc
            self.tld = self.netloc

def get_netloc(url):
    u = urlparse(url)
    return u.netloc, u.scheme


def get_domain(url):
    try:
        return get_fld(url)
    except Exception:
        host, scheme = get_netloc(url)
        return host


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


if __name__ == "__main__":
    u1 = "http://www.baidu.com"
    print(get_domain(u1))

    u1 = "http://www.baidu.com:8888/"
    print(get_netloc(u1), get_domain(u1))

    u1 = "http://www.hust.edu.cn"
    print(get_domain(u1))

    u1 = "http://sse.hust.edu.cn"
    print(get_domain(u1))

    u1 = "https://192.168.1.1:5555"
    print(get_domain(u1))

    u = URL("http://www.baidu.com:8888/")
    print(u.host, u.port, u.fld)
