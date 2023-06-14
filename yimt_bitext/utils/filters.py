import difflib
import itertools
import string

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


class NonZeroNumeralsFilter(Filter):
    """Similarity measure between numerals of the two sentences with zeros removed

    If require_all is True, all scores (for pairs of n segments) have
    to be equal or above the threshold; otherwise at least one the
    scores have to be equal or above the threshold. For bilingual
    input, it has no effect.

    See :cite:`vazquez-etal-2019-university`

    """

    def __init__(self, threshold=0.5, require_all=True):
        self.threshold = threshold
        self.require_all = require_all

    def score(self, pair):
        nums = [[int(c) for c in sent if c in string.digits and c != '0']
                for sent in pair]
        ratios = []
        for num1, num2 in itertools.combinations(nums, 2):
            seq = difflib.SequenceMatcher(None, num1, num2)
            ratios.append(seq.ratio())
        return ratios

    def filter(self, src, tgt):
        score = self.score((src, tgt))
        if self.require_all:
            if all(ratio >= self.threshold for ratio in score):
                return src, tgt
            else:
                return None
        if any(ratio >= self.threshold for ratio in score):
            return src, tgt
        else:
            return None


class RepetitionFilter(Filter):
    """Filter segments with repeated content

    Filter segments with substrings of min_length to max_length
    characters that are repeated at least threshold number of times.
    The first occurrence is not counted to the threshold, i.e.,
    threshold 2 means that the substring has to occur three times.

    There may be optional space character(s) between the repeated
    strings that are not counted to the length. The repeated string
    cannot start with a whitespace character but is not limited
    otherwise.

    """

    def __init__(self, threshold=2, min_length=3, max_length=16, **kwargs):
        self._threshold = threshold
        self._min_length = min_length
        self._max_length = max_length
        self._regexp = self._get_regexp()
        super().__init__(**kwargs)

    @property
    def min_length(self):
        """Minimum number of characters in pattern"""
        return self._min_length

    @property
    def max_length(self):
        """Maximum number of characters in pattern"""
        return self._max_length

    @property
    def threshold(self):
        """Threshold for the number of repetitions"""
        return self._threshold

    def _get_regexp(self):
        """Return compiled regexp for finding repetitions"""
        rstring = f'(\\S.{{{self.min_length-1},{self.max_length}}}?)(?: *\\1){{{self.threshold},}}'
        return regex.compile(rstring)

    def get_repetitions(self, segment):
        """Return the number of repetitions and the repeated string

        Returns the number of repetitions and the repeated string for
        the first match of at least self.threshold number of
        repetitions. The segment may contain longer repetitions than
        the one returned. If there no matched repetitions, zero and
        None are returned.

        """
        match = self._regexp.search(segment)
        if match:
            full = match.group(0)
            repeated = match.group(1)
            return full.count(repeated) - 1, repeated
        return 0, None

    def score(self, pair):
        return [self.get_repetitions(sent)[0] for sent in pair]

    def filter(self, src, tgt):
        score = self.score((src, tgt))
        if all(repetitions < self.threshold for repetitions in score):
            return src, tgt
        else:
            return None


def filter_file(in_path, filters, out_path=None, logger=None):
    if out_path is None:
        out_path = in_path + ".filtered"

    total = 0
    passed = 0

    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {} Passed: {}".format(total, passed))
            line = line.strip()
            cols = line.split("\t")
            if len(cols) >= 2:
                src, tgt = cols[:2]
            else:
                if logger:
                    logger.warning("NO Pair: {}".format(line))
                continue

            valid = True
            for f in filters:
                if f.filter(src, tgt) is None:
                    if logger:
                        logger.debug("{}: {}".format(f.__class__.__name__, line))
                    valid = False
                    break
            if valid:
                passed += 1
                out_f.write(line + "\n")

    if logger:
        logger.info("Total: {} Passed: {}".format(total, passed))

    return out_path


if __name__ == "__main__":
    same_filter = SameFilter()
    print(same_filter.filter("i like it", "i like it"))
    print(same_filter.filter("i like it", " like it"))
    print(same_filter.filter("i like it", "I like it "))
    print(same_filter.filter("我喜欢", "我喜欢"))

    print()

    empty_filter = EmptyFilter()
    print(empty_filter.filter("", " "))
    print(empty_filter.filter(" a test", " "))
    print(empty_filter.filter("a test", "just a test"))

    print()

    overlap_filter = OverlapFilter(ratio=0.5)
    print(overlap_filter.filter("abcdef", "abcdef"))
    print(overlap_filter.filter("啊啊啊", "啊啊啊"))
    print(overlap_filter.filter("aaaaaaa", "aaa啊啊啊啊啊啊阿"))

    print()
    lang_filter = LangFilter("en", "zh")
    print(lang_filter.filter("i like it", "i like it"))
    print(lang_filter.filter("i like it", "我真的很喜欢它。"))

    print()

    new_len_filter = LengthFilter(src_len_fn=LengthFilter.space_sep_len_f,
                                  tgt_len_fn=LengthFilter.space_sep_len_f,
                                  src_lens=(2, 4), tgt_lens=(2, 7),
                                  ratio=3)
    print(new_len_filter.filter("like", "what what are wrong"))
    print(new_len_filter.filter("a b", "aaaaa bbbb cccc"))
    print(new_len_filter.filter("a b", "aaaaa bbbb ccccdddddddddd ff ee dd f"))

    print()

    new_len_filter2 = LengthFilter(src_len_fn=LengthFilter.space_sep_len_f,
                                  tgt_len_fn=LengthFilter.char_len_f,
                                  src_lens=(2, 4), tgt_lens=(2, 7),
                                  ratio=3)
    print(new_len_filter2.filter("a b", "啊啊啊啊啊啊啊啊啊啊啊啊"))
    print(new_len_filter2.filter("a b", "啊啊啊啊"))

    print()

    alphabet_filter = AlphabetRatioFilter(threshold=0.8, exclude_whitespace=True)
    print(alphabet_filter.filter("a b cddd", "啊啊 啊啊啊啊"))
    print(alphabet_filter.filter("a b cddd", "啊啊 啊啊啊啊+++++"))
    print(alphabet_filter.filter("a b cddd09999999555", "啊啊 啊啊啊啊"))

    print()

    char_filter = CharacterRatioFilter(scripts=("Latin", "Han"), thresholds=(0.8, 0.8))
    print(char_filter.filter("a b cddd", "啊啊 啊啊啊啊+++++++"))
    print(char_filter.filter("a b cddd啊啊啊啊", "啊啊 啊啊啊啊"))

    print()
    t1 = "abc 132"
    t2 = "dddddd 233"
    t3 = "eeee 132"
    number_filter = NonZeroNumeralsFilter(threshold=1.0)
    print(number_filter.filter(t1, t2))
    print(number_filter.filter(t1, t3))

    print()
    rep_filter = RepetitionFilter()
    print(rep_filter.filter("abcd abcd abcd what what", "how are you"))
    print(rep_filter.filter("aaaa", "how are you"))