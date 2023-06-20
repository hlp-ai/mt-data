import sys

import pysbd
from indicnlp.tokenize.sentence_tokenize import sentence_split
from sentence_splitter import split_text_into_sentences


def split_sentences(text, lang="en"):
    """Segment paragraph into sentences

    Args:
        text: paragraph string
        lang: language code string

    Returns:
        list of sentences
    """
    languages_splitter = ["ca", "cs", "da", "de", "el", "en", "es", "fi", "fr", "hu", "is", "it",
                          "lt", "lv", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr"]
    languages_indic = ["as", "bn", "gu", "hi", "kK", "kn", "ml", "mr", "ne", "or", "pa", "sa",
                       "sd", "si", "ta", "te"]
    languages_pysbd = ["en", "hi", "mr", "zh", "es", "am", "ar", "hy", "bg", "ur", "ru", "pl",
                       "fa", "nl", "da", "fr", "my", "el", "it", "ja", "de", "kk", "sk"]

    languages = languages_splitter + languages_indic + languages_pysbd
    lang = lang if lang in languages else "en"

    text = text.strip()

    if lang in languages_pysbd:
        segmenter = pysbd.Segmenter(language=lang, clean=True)
        sentences = segmenter.segment(text)
    elif lang in languages_splitter:
        sentences = split_text_into_sentences(text, lang)
    elif lang in languages_indic:
        sentences = sentence_split(text, lang)

    return sentences


def split_sent_file(fn, out_path=None, lang="en"):
    if out_path is None:
        out_path = fn + ".sent"

    with open(fn, encoding="utf-8") as f1, open(out_path, "w", encoding="utf-8") as out:
        for p in f1:
            p = p.strip()
            sentences = sentence_split(p, lang)
            for s in sentences:
                out.write(s + "\n")

    return out_path


if __name__ == "__main__":
    fn = sys.argv[1]
    lang = sys.argv[2]

    split_sent_file(fn, lang=lang)
