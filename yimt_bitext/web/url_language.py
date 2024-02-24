import re


class UrlLanguage(object):

    def __init__(self, strip_query_variables=False, map_file="./langs-map.txt"):
        self._strip_query_variables = []
        if strip_query_variables:
            self._strip_query_variables = [
                'lang', 'clang', 'language', 'locale', 'selectedLocale']
        self.code_to_language = {}

        with open(map_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                parts = line.split(",")
                for i in range(len(parts)):
                    self.code_to_language[parts[i]] = parts[0]
        # # These should all be lower-case, matching is case-insensitive
        # for code in ['bulgarian', 'bul', 'bg']:
        #     self.code_to_language[code] = 'bg'
        # for code in ['breton', 'bre', 'br']:
        #     self.code_to_language[code] = 'br'
        # for code in ['malay', 'ms']:
        #     self.code_to_language[code] = 'ms'
        # for code in ['italian', 'italiano', 'ital', 'ita', 'it-it', 'it-ch',
        #              'it']:
        #     self.code_to_language[code] = 'it'
        # for code in ['portuguese', 'portugues', 'pt-pt', 'pt-br', 'ptg', 'ptb', 'pt']:
        #     self.code_to_language[code] = 'pt'
        # for code in ['russian', 'russkiy', 'ru-ru', 'rus', 'ru']:
        #     self.code_to_language[code] = 'ru'
        # for code in ['dutch', 'nederlands', 'nl-nl', 'nld', 'dut', 'nl']:
        #     self.code_to_language[code] = 'nl'
        # for code in ['romanian', 'romana', 'romlang', 'rom', 'ro-ro', 'ro']:
        #     self.code_to_language[code] = 'ro'
        # for code in ['soma', 'som', 'so', 'somal', 'somali', 'so-so',
        #              'af-soomaali', 'soomaali']:
        #     self.code_to_language[code] = 'so'
        # for code in ['finnish', 'finnisch', 'fin', 'suomi', 'suomeksi',
        #              'suominen', 'suomija', 'fi-fi', 'fi']:
        #     self.code_to_language[code] = 'fi'
        # for code in ['greek', 'el', 'ell', 'gre', 'el_gr']:  # 现代希腊语
        #     self.code_to_language[code] = 'el'
        # for code in ['latin', 'la', 'lat']:  # 拉丁语
        #     self.code_to_language[code] = 'la'
        # for code in ['norwegian', 'Norsk', 'no', 'nor', 'no_no', 'no_no_ny']:
        #     self.code_to_language[code] = 'no'
        # for code in ['swedish', 'svenska', 'sv', 'swe', 'sv_se']:  # 瑞典语
        #     self.code_to_language[code] = 'sv'
        # for code in ['burmese', 'my', 'mya', 'bur']:  # 缅甸语
        #     self.code_to_language[code] = 'my'
        # for code in ['tibetan', 'bo', 'bod', 'tib']:  # 藏语
        #     self.code_to_language[code] = 'bo'
        # for code in ['belarusian', 'be', 'bel', 'be_by']:  # 白俄罗斯语
        #     self.code_to_language[code] = 'be'
        # for code in ['croatian', 'hr', 'hrv', 'hr_hr']:  # 克罗地亚语
        #     self.code_to_language[code] = 'hr'
        #
        # for code in ['macedonian', 'mk', 'mkd', 'mac']:  # 马其顿语
        #     self.code_to_language[code] = 'mk'
        # for code in ['icelandic', 'is', 'isl', 'ice']:   # 冰岛语
        #     self.code_to_language[code] = 'is'
        # for code in ['slovenian', 'sl', 'slv']:   # 斯洛文尼亚语
        #     self.code_to_language[code] = 'sl'
        # for code in ['slovak', 'sl', 'slk', 'slo']:   # 斯洛伐克语
        #     self.code_to_language[code] = 'sk'
        # for code in ['sinhala', 'sinhalese', 'si', 'sin']:   # 僧加罗语
        #     self.code_to_language[code] = 'si'
        # for code in ['afrikaans', 'af', 'afr']:   # 南非语
        #     self.code_to_language[code] = 'af'
        # for code in ['tagalog', 'tl', 'tgl']:   # 他加禄语
        #     self.code_to_language[code] = 'tl'
        # for code in ['malagasy', 'ml', 'mlg']:   # 马达加斯加语
        #     self.code_to_language[code] = 'ml'
        # for code in ['tegula', 'te', 'tel']:   # 泰卢固语
        #     self.code_to_language[code] = 'te'

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
