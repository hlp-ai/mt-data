"""将TSV平行语料文件分成两个单语文本文件"""
import argparse
import io


def pair_to_single(pair_path, src_path, tgt_path):
    """Split a parallel file into source ang target file"""
    src_f = io.open(src_path, "w", encoding="utf-8")
    tgt_f = io.open(tgt_path, "w", encoding="utf-8")

    tsv_f = io.open(pair_path, encoding="utf-8")
    cnt = 0
    for line in tsv_f:
        line = line.strip()
        if len(line) == 0:
            continue
        p = line.split("\t")
        if len(p) >= 2:
            src_f.write(p[0] + "\n")
            tgt_f.write(p[1] + "\n")

        cnt += 1
        if cnt % 500000 == 0:
            print(cnt)

    print(cnt)
    src_f.close()
    tgt_f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("tsv_fn")
    argparser.add_argument("src_fn")
    argparser.add_argument("tgt_fn")
    args = argparser.parse_args()

    pair_fn = args.tsv_fn
    src_fn = args.src_fn
    tgt_fn = args.tgt_fn

    pair_to_single(pair_fn, src_fn, tgt_fn)


