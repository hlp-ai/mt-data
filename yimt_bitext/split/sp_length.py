import os

from yimt_bitext.split.sp import load_spm, tokenize

sp_nllb200 = load_spm(os.path.join(os.path.dirname(__file__), "flores200_sacrebleu_tokenizer_spm.model"))


def length_subword(txt):
    """文本的子词长度"""
    tokens = tokenize(sp_nllb200, txt)
    return len(tokens[0])


if __name__ == "__main__":
    print(length_subword("今天下好大的雪呀。"))
    print(length_subword("This is a book."))
