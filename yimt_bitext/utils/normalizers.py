import re

import zhconv

from yimt_bitext.utils.chars import is_ascii_char, is_en_punct
from yimt_bitext.utils.clean import clean_text


def detok_zh_str(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == " ":
            if (i > 0 and is_en_punct(s[i-1])) or (i < len(s)-1 and is_en_punct(s[i+1])):
                i += 1
                continue

            if (i > 0 and is_ascii_char(s[i-1])) and (i < len(s)-1 and is_ascii_char(s[i+1])):
                result += " "
        else:
            result += s[i]
        i += 1

    return result


def hant_2_hans(hant_str: str):
    """Traditional Chinese to Simplified Chinese"""
    return zhconv.convert(hant_str, 'zh-hans')


class Normalizer(object):

    def normalize(self, s):
        """Normalize text

        Args:
            s: string
        Returns:
            the normalize string
        """
        pass


class Cleaner(Normalizer):
    def normalize(self, s):
        s = s.strip()
        s = clean_text(s)
        s = re.sub(r"\s{2,}", " ", s)
        return s


class DeTokenizer(Normalizer):
    """Remove unnecessary spaces"""

    def normalize(self, s):
        s = s.strip()
        s = detok_zh_str(s)
        return s


punct_pairs = [('“', '”'), ('"', '"'), ("‘", "’"), ("（", "）"), ("《", "》"), ("(", ")")]


def normalize_pair_punct(s, left_punct, right_punct):
    s = s.replace(left_punct + left_punct, "")
    s = s.replace(left_punct + left_punct + left_punct, left_punct)

    s = s.replace(right_punct + right_punct, "")
    s = s.replace(right_punct + right_punct + right_punct, right_punct)

    idx = s.find(left_punct)
    if idx >= 0:
        has_pair = s.find(right_punct, idx + 1)
        if has_pair == -1:
            s = s[:idx] + s[idx + 1:]
            # s = s.replace(left_punct, "")

    idx = s.find(right_punct)
    if idx >= 0:
        has_pair = s.find(left_punct, 0, idx)
        if has_pair == -1:
            s = s[:idx] + s[idx + 1:]
            # s = s.replace(right_punct, "")

    return s


class PairPunctNormalizer(Normalizer):

    def normalize_pair(self, s):
        for p in punct_pairs:
            s = normalize_pair_punct(s, p[0], p[1])

        return s

    def normalize(self, s):
        s = self.normalize_pair(s)
        return s


class Hant2Hans(Normalizer):
    """Traditional Chinese to Simplified Chinese"""

    def normalize(self, s):
        s = hant_2_hans(s)

        return s
