import os
import shutil
import sys

if __name__ == "__main__":
    to_zh_dir = sys.argv[1]
    yue_dir = sys.argv[2]
    if not os.path.exists(yue_dir):
        os.makedirs(yue_dir, exist_ok=True)

    for root, dirs, names in os.walk(to_zh_dir):
        for filename in names:
            corpus = os.path.join(root, filename)
            if corpus.lower().find("qed") >=0 or corpus.lower().find("ted2020") >= 0:
                shutil.move(corpus, yue_dir)
