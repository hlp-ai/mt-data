import regex

from yimt_bitext.utils.lang import detect_lang


class Filter(object):
    """Parallel corpus filter base class"""

    def filter(self, src, tgt):
        """

        Args:
            src: source sentence
            tgt: target sentence
        Returns:
            None if invalid, otherwise pair
        """
        pass


class EmptyFilter(Filter):
    """Filter pair whose source or target is empty"""

    def filter(self, src, tgt):
        if len(src.strip()) == 0 or len(tgt.strip()) == 0:
            return None

        return src, tgt


class SameFilter(Filter):
    """Filter pair with same source and target"""

    def __init__(self, lower=True):
        self._lower = lower

    def filter(self, src, tgt):
        if self._lower:
            if src.strip().lower() == tgt.strip().lower():
                return None
        else:
            if src.strip() == tgt.strip():
                return None

        return src, tgt


class OverlapFilter(Filter):
    """Filter pair whose source and target have too much overlap"""

    def __init__(self, ratio=0.8):
        self._ratio = ratio

    def filter(self, src, tgt):
        import difflib

        s = difflib.SequenceMatcher(None, src, tgt)
        if s.ratio() > self._ratio:
            return None
        return src, tgt


class LangFilter(Filter):
    """Filter pair with wrong language"""

    def __init__(self, src_lang, tgt_lang):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def filter(self, src, tgt):
        if detect_lang(src) != self.src_lang or detect_lang(tgt) != self.tgt_lang:
            return None

        return src, tgt


class LengthFilter(Filter):

    space_sep_len_f = lambda s: len(s.split())
    char_len_f = lambda s: len(s)

    def __init__(self, src_len_fn=len, tgt_len_fn=len,
                 src_lens=(None, None), tgt_lens=(None, None),
                 ratio=3):
        self.src_min_len = src_lens[0]
        self.src_max_len = src_lens[1]
        self.tgt_min_len = tgt_lens[0]
        self.tgt_max_len = tgt_lens[1]

        self.src_len_fn = src_len_fn
        self.tgt_len_fn = tgt_len_fn

        self.ratio = ratio

    def filter(self, src, tgt):
        src_len = self.src_len_fn(src)
        tgt_len = self.tgt_len_fn(tgt)

        if self.src_min_len is not None and src_len < self.src_min_len:
            return None
        if self.src_max_len is not None and src_len > self.src_max_len:
            return None
        if self.tgt_min_len is not None and tgt_len < self.tgt_min_len:
            return None
        if self.tgt_max_len is not None and tgt_len > self.tgt_max_len:
            return None

        if src_len <= self.ratio * tgt_len and tgt_len <= self.ratio * src_len:
            return src, tgt
        else:
            return None


class AlphabetRatioFilter(Filter):
    """Proportion of alphabetic characters in the segment"""

    def __init__(self, threshold=0.75, exclude_whitespace=False):
        self.threshold = threshold
        self.exclude_whitespace = exclude_whitespace
        self.re_whitespace = regex.compile(r'\s')
        self.re_not_alphas = regex.compile(r'\p{Alphabetic=No}')

    def filter(self, src, tgt):
        if self.score(src) >= self.threshold and self.score(tgt) >= self.threshold:
            return src, tgt

        return None

    def score(self, s):
        segment = s
        if self.exclude_whitespace:
            segment = self.re_whitespace.sub('', s)
        alphas = self.re_not_alphas.sub('', s)
        r = len(alphas) / len(segment)
        return r


class CharacterRatioFilter(Filter):
    """Proportion of alphabetic characters that are in the given script

    For a list of valid scripts, see e.g.
    https://www.regular-expressions.info/unicode.html

    """
    lang2script = {
        "zh": "Han",
        "en": "Latin",
        "ko": "Hangul"
    }

    def __init__(self, scripts, thresholds=None):
        self.scripts = scripts
        self.thresholds = [1] * len(scripts) if thresholds is None else thresholds
        self.re_not_alphas = regex.compile(r'\p{Alphabetic=No}')
        self.re_not_script = [regex.compile(fr'\p{{^Script={script}}}')
                              for script in self.scripts]

    def score(self, sent, idx):
        alphas = self.re_not_alphas.sub('', sent)
        if alphas:
            script = self.re_not_script[idx].sub('', alphas)
            return len(script) / len(alphas)
        else:
            return 0.0

    def filter(self, src, tgt):
        if self.score(src, 0) < self.thresholds[0] or self.score(tgt, 1) < self.thresholds[1]:
            return None

        return src, tgt
