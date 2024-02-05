from yimt_bitext.utils.lang import detect_lang

import re

from yimt_bitext.normalize.normalizers import detok_zh_str

tokenizers = {}


def _get_tokenizer(lang):
    """Get tokenizer for given language

    Args:
        lang: language code string

    Returns:
        tokenizer of some type
    """
    if lang in tokenizers:
        return tokenizers.get(lang)

    print("Loading tokenizer for", lang)

    if lang == "ko":
        # from konlpy.tag import Mecab
        # tokenizer = Mecab()
        # TODO this tokenizer conflict with ctranslate2, because it uses CUDA
        from hangul.tokenizer import WordSegmenter
        tokenizer = WordSegmenter()
    elif lang == "ja":
        import fugashi
        tokenizer = fugashi.Tagger()
        # import Mykytea
        # opt = "-model jp-0.4.7-1.mod"
        # tokenizer = Mykytea.Mykytea(opt)
    elif lang == "zh_cn" or lang == "zh":
        # import Mykytea
        # opt = "-model ctb-0.4.0-1.mod"
        # tokenizer = Mykytea.Mykytea(opt)
        # import jieba
        # tokenizer = jieba
        import jieba
        tokenizer = jieba
    elif lang == "zh_tw":
        import jieba
        tokenizer = jieba
    elif lang == "vi":
        from pyvi import ViTokenizer
        tokenizer = ViTokenizer
    elif lang == "th":
        from pythainlp.tokenize import word_tokenize
        tokenizer = word_tokenize
    elif lang == "ar":
        import pyarabic.araby as araby
        tokenizer = araby
    # elif lang=="en":
    #     from nltk import word_tokenize
    #     tokenizer = word_tokenize
    else:
        from nltk.tokenize import ToktokTokenizer
        tokenizer = ToktokTokenizer()

    tokenizers[lang] = tokenizer

    return tokenizer


def word_segment(sentence, lang):
    """Segment sentence into tokens

    Args:
        sentence: sentence
        lang: language code string

    Returns:
        token list
    """
    tokenizer = _get_tokenizer(lang)
    if lang == 'ko':
        # words = [word for word, _ in tokenizer.pos(sent)]
        tokenizer.inputAsString(sentence)
        tokenizer.doSegment()
        toks = tokenizer.segmentedOutput
        words = toks.split()
    elif lang == 'ja':
        # words = [elem for elem in tokenizer.getWS(sent)]
        words = [word.surface for word in tokenizer(sentence)]
    elif lang == 'th':
        words = tokenizer(sentence, engine='mm')
    elif lang == 'vi':
        words = tokenizer.tokenize(sentence).split()
    elif lang == 'zh_cn' or lang == "zh":
        words = list(tokenizer.cut(sentence, cut_all=False))
    elif lang == "zh_tw":
        words = list(tokenizer.cut(sentence, cut_all=False))
    elif lang == "ar":
        words = tokenizer.tokenize(sentence)
    # elif lang=="en":
    #     words = tokenizer(sent)
    else:  # Most european languages
        sentence = re.sub("([A-Za-z])(\.[ .])", r"\1 \2", sentence)
        words = tokenizer.tokenize(sentence)

    return words


def tokenize_single(in_fn, lang=None, out_fn=None):
    if out_fn is None:
        out_fn = in_fn + ".pretok"

    if lang is None:
        with open(in_fn, encoding="utf-8") as in_f:
            txt = in_f.read(128)
            lang = detect_lang(txt)
            print("Language detected:", lang)

    out_f = open(out_fn, "w", encoding="utf-8")
    n = 0
    with open(in_fn, encoding="utf-8") as in_f:
        for line in in_f:
            line = line.strip()
            toks = word_segment(line, lang=lang)
            out_f.write(" ".join(toks) + "\n")
            n += 1
            if n % 50000 == 0:
                print(n)
    print(n)
    out_f.close()

    return out_fn


def detok_zh(in_file, out_file=None):
    if out_file is None:
        out_file = in_file + ".detok"

    outf = open(out_file, "w", encoding="utf-8")

    with open(in_file, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            line = re.sub(r"\s{2,}", " ", line)
            line = line.strip()
            line = detok_zh_str(line)
            outf.write(line + "\n")

    outf.close()


def detok_zh_file(in_file, out_file=None):
    if out_file is None:
        out_file = in_file + ".detok"

    outf = open(out_file, "w", encoding="utf-8")

    with open(in_file, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            line = re.sub(r"\s{2,}", " ", line)
            line = line.strip()
            line = detok_zh_str(line)
            outf.write(line + "\n")

    outf.close()
