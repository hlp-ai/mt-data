import sys

from yimt_bitext.opus.utils import interset

if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    out = sys.argv[3]

    interset(f1, f2, out, "SRCTGT")