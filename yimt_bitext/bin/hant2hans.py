"""Convert file in traditional Chinese into file in simplified Chinese"""
import argparse
import io

from yimt_bitext.utils.normalizers import hant_2_hans


def hant2s_file(in_fn, out_fn):
    in_f = io.open(in_fn, encoding="utf-8")
    out_f = io.open(out_fn, "w", encoding="utf-8")

    cnt = 0
    for line in in_f:
        line = line.strip()
        line_s = hant_2_hans(line)
        out_f.write(line_s + "\n")

        cnt += 1
        if cnt % 100000 == 0:
            print(cnt)

    out_f.close()

    print(cnt)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    in_f = io.open(args.in_fn, encoding="utf-8")
    out_f = io.open(args.out_fn, "w", encoding="utf-8")

    cnt = 0
    for line in in_f:
        line = line.strip()
        line_s = hant_2_hans(line)
        out_f.write(line_s + "\n")

        cnt += 1
        if cnt % 100000 == 0:
            print(cnt)

    print(cnt)
