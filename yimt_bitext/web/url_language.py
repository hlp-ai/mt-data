import re


class UrlLanguage(object):

    def __init__(self, strip_query_variables=False):
        self._strip_query_variables = []
        if strip_query_variables:
            self._strip_query_variables = [
                'lang', 'clang', 'language', 'locale', 'selectedLocale']
        self.code_to_language = {}
        # These should all be lower-case, matching is case-insensitive
        for code in ['arabic', 'ara', 'ar']:
            self.code_to_language[code] = 'ar'
        for code in ['bulgarian', 'bul', 'bg']:
            self.code_to_language[code] = 'bg'
        for code in ['breton', 'bre', 'br']:
            self.code_to_language[code] = 'br'
        for code in ['czech', 'cze', 'cz', 'cs']:
            self.code_to_language[code] = 'cs'
        for code in ['danish', 'da-dk', 'dan', 'da']:
            self.code_to_language[code] = 'da'
        for code in ['deutsch', 'german', 'ger', 'deu', 'de-at', 'de-ch', 'de-de', 'de-lu', 'de']:
            self.code_to_language[code] = 'de'
        for code in ['english', 'eng', 'en']:
            self.code_to_language[code] = 'en'
        for code in ['espanol', 'spanish', 'spa', 'esp', 'es']:
            self.code_to_language[code] = 'es'
        for code in ['french', 'francais', 'fran', 'fra', 'fre', 'fr']:
            self.code_to_language[code] = 'fr'
        for code in ['chinese', 'chi', 'zh', "zho"]:
            self.code_to_language[code] = 'zh'
        for code in ['japanese', 'ja', 'ja-jp']:
            self.code_to_language[code] = 'jp'
        for code in ['vietnamese', 'vi', 'vi-vn']:
            self.code_to_language[code] = 'vi'
        for code in ['korean', 'ko', 'ko-kr', "kor"]:
            self.code_to_language[code] = 'ko'
        for code in ['malay', 'ms']:
            self.code_to_language[code] = 'ms'
        for code in ['tedesco', 'de-de', 'de-ch', 'de-at', 'de-li', 'de-lu',
                     'allemand']:
            self.code_to_language[code] = 'de'
        for code in ['fr-be', 'fr-ca', 'fr-fr', 'fr-lu', 'fr-ch', 'f']:
            self.code_to_language[code] = 'fr'
        for code in ['italian', 'italiano', 'ital', 'ita', 'it-it', 'it-ch',
                     'it']:
            self.code_to_language[code] = 'it'
        for code in ['portuguese', 'portugues', 'pt-pt', 'pt-br', 'ptg', 'ptb', 'pt']:
            self.code_to_language[code] = 'pt'
        for code in ['russian', 'russkiy', 'ru-ru', 'rus', 'ru']:
            self.code_to_language[code] = 'ru'
        for code in ['dutch', 'nederlands', 'nl-nl', 'nld', 'dut', 'nl']:
            self.code_to_language[code] = 'nl'
        for code in ['en-en', 'en-us', 'en-uk', 'en-ca', 'en-bz', 'en-ab',
                     'en-in', 'en-ie', 'en-jm', 'en-nz', 'en-ph', 'en-za',
                     'en-tt', 'gb', 'en-gb', 'inglese', 'englisch', 'us']:
            self.code_to_language[code] = 'en'
        for code in ['romanian', 'romana', 'romlang', 'rom', 'ro-ro', 'ro']:
            self.code_to_language[code] = 'ro'
        for code in ['soma', 'som', 'so', 'somal', 'somali', 'so-so',
                     'af-soomaali', 'soomaali']:
            self.code_to_language[code] = 'so'
        for code in ['turkish', 'tur', 'turkic', 'tr-tr', 'tr']:
            self.code_to_language[code] = 'tr'
        for code in ['finnish', 'finnisch', 'fin', 'suomi', 'suomeksi',
                     'suominen', 'suomija', 'fi-fi', 'fi']:
            self.code_to_language[code] = 'fi'
        for code in ['thailand', 'th-th', 'thai', 'th']:
            self.code_to_language[code] = 'th'

        pairs = list(self.code_to_language.items())

        for code, lang in pairs:
            # add de_de from de-de
            self.code_to_language[code.replace('-', '_')] = lang

        keys = self.code_to_language.keys()
        regexp_string = '(?<![a-zA-Z0-9])(?:%s)(?![a-zA-Z0-9])' % ('|'.join(keys))
        self.re_code = re.compile(regexp_string, re.IGNORECASE)

    def find_language(self, uri):
        for match in self.re_code.findall(uri):
            match = match.lower()
            assert match in self.code_to_language, 'Unknown match: %s\n' % match
            return self.code_to_language[match]
        return ''

    def normalize_lang_code(self, lang_code):
        if lang_code in self.code_to_language:
            return self.code_to_language[lang_code]
        else:
            return None


if __name__ == '__main__':
    url_language = UrlLanguage()

    uri = "http://ko.abc.com/"
    lang = url_language.find_language(uri)
    print(lang)

    uri = "http://www.abc.com/kor/a.html"
    lang = url_language.find_language(uri)
    print(lang)

    uri = "http://www.abc.com/p/a.html?t=kor"
    lang = url_language.find_language(uri)
    print(lang)

    uri = "http://www.abc.com/p/kora.jsp"
    lang = url_language.find_language(uri)
    print(lang)

    while True:
        uri = input("input url: ")
        lang = url_language.find_language(uri)
        print(lang)
