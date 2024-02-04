"""将繁体中文转换成简体中文"""
import argparse

from yimt_bitext.utils.normalizers import hant_2_hans


def hant2s_file(in_fn, out_fn):
    cnt = 0
    with open(in_fn, encoding="utf-8") as in_f, open(out_fn, "w", encoding="utf-8") as out_f:
        for line in in_f:
            line = line.strip()
            line_s = hant_2_hans(line)
            out_f.write(line_s + "\n")

            cnt += 1
            if cnt % 100000 == 0:
                print(cnt)

    print(cnt)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    hant2s_file(args.in_fn, args.out_fn)
