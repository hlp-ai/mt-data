"""5. Preprocess sentence files"""
import os
import sys

from yimt_bitext.utils.clean import clean_file
from yimt_bitext.utils.dedup import dedup_file
from yimt_bitext.utils.text_splitter import split_sent_file

if __name__ == "__main__":
    domain_dir = sys.argv[1]
    sents_dir = os.path.join(domain_dir, "lang2sents")

    for f in os.listdir(sents_dir):
        if not f.endswith(".txt"):
            continue
        lang = os.path.basename(f)
        f = os.path.join(sents_dir, f)
        print("Cleaning {}...".format(f))
        out = clean_file(f)

        print("Splitting {}...".format(out))
        out = split_sent_file(out, lang=lang)

        print("Deduping {}...".format(out))
        dedup_file(out)
