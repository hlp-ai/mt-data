"""将互为翻译的两个单语文本文件合并为TSV格式平行语料文件"""
import argparse
import os

from yimt_bitext.utils.count import same_lines


def single_to_pair(src_path, tgt_path, pair_path, logger_opus=None):
    """Combine source and target file into a parallel one"""
    if logger_opus:
        logger_opus.info("Merge {} {} into {}".format(src_path, tgt_path, pair_path))
    assert same_lines(src_path, tgt_path)

    cnt = 0
    with open(src_path, encoding="utf-8") as src_f, open(tgt_path, encoding="utf-8") as tgt_f, open(pair_path, "w", encoding="utf-8") as out_f:
        for p in zip(src_f, tgt_f):
            out_f.write(p[0].strip() + "\t" + p[1].strip() + "\n")
            cnt += 1
            if cnt % 100000 == 0:
                if logger_opus:
                    logger_opus.info("{}: {}".format(pair_path, cnt))

        if logger_opus:
            logger_opus.info("{}: {}".format(pair_path, cnt))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src_fn")
    parser.add_argument("tgt_fn")
    parser.add_argument("out_fn")
    args = parser.parse_args()

    src_fn = args.src_fn
    tgt_fn = args.tgt_fn
    out_fn = args.out_fn

    out_path = os.path.dirname(out_fn)
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    single_to_pair(src_fn, tgt_fn, out_fn)

