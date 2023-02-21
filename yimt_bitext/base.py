"""Interface for core concepts"""


class UrlsCrawled:

    def is_crawled(self, url):
        """Is the url crawled?"""
        pass

    def crawled(self, url):
        """The url has been crawled"""
        pass


class UrlsToCrawl:

    def add(self, url):
        """Add url to crawl"""
        pass

    def next(self):
        """Get url for crawling"""
        pass


class Crawler:

    def crawl(self, url):
        pass


class LangStat:

    def stat(self, text):
        pass


class LangID:

    def detect(self, text):
        pass


class SentenceSplitter:

    def split(self, text):
        pass


class Host2Lang2Len:

    def update(self, host, lang2len):
        """Update the language statistics of given host"""
        pass

    def get(self, host):
        """Get the language statistics of given host"""
        pass

    def next(self):
        """Iterate"""
        pass


class MultiLangHost:

    def update(self, host, lang):
        """Add lang to lang list of host"""
        pass

    def get(self, host):
        """Get the lang list of host"""
        pass

    def next(self):
        """Iterate"""
        pass


class Host2Lang2Sent:

    def update(self, host, lang, sentences):
        pass

    def get(self, host, lang):
        pass


class ProcessedWET:

    def is_processed(self, wet_url):
        pass

    def processed(self, wet_url):
        pass


class WETs:

    def add(self, cc_id):
        pass

    def next(self):
        pass