"""5. Preprocess sentence files"""
import os
import sys

from yimt_bitext.utils.clean import clean_file
from yimt_bitext.utils.dedup import dedup_file

if __name__ == "__main__":
    domain_dir = sys.argv[1]
    sents_dir = os.path.join(domain_dir, "lang2sents")

    for f in os.listdir(sents_dir):
        f = os.path.join(sents_dir, f)
        print("Cleaning {}".format(f))
        out = clean_file(f)
        print("Deduping {}".format(out))
        dedup_file(out)
