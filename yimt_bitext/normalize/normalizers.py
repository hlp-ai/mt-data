import re

import yaml
import zhconv
import html
from regex import regex

from yimt_bitext.utils.chars import is_ascii_char, is_en_punct
from yimt_bitext.utils.clean import clean_text


not_letter = regex.compile(r'[^\p{L}]')


def norm(s, lower=True, remove_noletter=True):
    if lower:
        s = s.lower()

    if remove_noletter:
        s = regex.sub(not_letter, "", s)
    return s


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


def detok_zh_file_inplace(in_file):
    lines = []
    with open(in_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            line = re.sub(r"\s{2,}", " ", line)
            line = line.strip()
            lines.append(line)

    with open(in_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(detok_zh_str(line) + "\n")


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

    def __init__(self, src=False, tgt=True):
        self.src = src
        self.tgt = tgt

    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        if self.src:
            src = detok_zh_str(src)
        if self.tgt:
            tgt = detok_zh_str(tgt)

        return src + "\t" + tgt


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

    def __init__(self, src=False, tgt=True):
        self.src = src
        self.tgt = tgt

    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        if self.src:
            src = hant_2_hans(src)
        if self.tgt:
            tgt = hant_2_hans(tgt)

        return src + "\t" + tgt


class ToZhNormalizer(Normalizer):

    def __init__(self):
        self.cleaner = Cleaner()

    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        src = self.cleaner.normalize(src)
        tgt = self.cleaner.normalize(tgt)
        tgt = hant_2_hans(tgt)

        return src + "\t" + tgt


class CleanerTSV(Normalizer):

    def __init__(self):
        self.cleaner = Cleaner()

    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        src = self.cleaner.normalize(src)
        tgt = self.cleaner.normalize(tgt)

        return src + "\t" + tgt


class HTMLEntityUnescape(Normalizer):

    def __init__(self, src=False, tgt=True):
        self.src = src
        self.tgt = tgt

    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        if self.src:
            src = html.unescape(src)
        if self.tgt:
            tgt = html.unescape(tgt)

        return src + "\t" + tgt


name2normalizer = {"CleanerTSV": CleanerTSV,
                   "DeTokenizer": DeTokenizer,
                   "Hant2Hans": Hant2Hans}


def load_normalizers(yml_file):
    with open(yml_file, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file.read())

        normalizers = []

        for f in config["normalizers"]:
            for k, v in f.items():
                class_name = k
                class_params = v["params"]
                if class_params:
                    normalizers.append(name2normalizer[class_name](**class_params))
                else:
                    normalizers.append(name2normalizer[class_name]())

        return normalizers
