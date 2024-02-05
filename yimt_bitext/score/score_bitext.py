import os
import sys
import time

from yimt_bitext.score.bitext_scorers import LaBSEScorer


def score_tsv(in_path, out_path=None,
         labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
         block=8, max_seq_len=48,
              clean_after_done=False, logger=None
         ):
    lines = open(in_path, encoding="utf-8").readlines()
    if logger:
        logger.info("{} # of lines: {}".format(in_path, len(lines)))

    if out_path is None:
        out_path = in_path + ".score"

    if os.path.exists(out_path):
        logger.info("{} exists".format(out_path))
        return out_path

    scorer = LaBSEScorer(labse_model_dir, max_seq_len)

    out_f = open(out_path, "w", encoding="utf-8")

    n = 0
    start = time.time()
    for i in range(0, len(lines), block):
        buf = lines[i:i+block]
        srcs = []
        tgts = []
        for line in buf:
            line = line.strip()
            pair = line.split("\t")
            if len(pair) != 2:
                continue
            src = pair[0]
            tgt = pair[1]
            srcs.append(src)
            tgts.append(tgt)

        ss = scorer.score(srcs, tgts)
        for j in range(len(ss)):
            out_f.write("{:.4f}\t{}\t{}\n".format(ss[j], srcs[j], tgts[j]))

        n += len(buf)
        if n % (40*block) == 0:
            t = time.time() - start
            if logger:
                logger.info("{} {}: {:.2f} pairs/sec".format(out_path, n, n/t))

    out_f.close()

    if clean_after_done:
        os.remove(in_path)

    return out_path


def main(in_path, out_path,
         labse_model_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1",
         block=8,
         max_seq_len=48
         ):
    scorer = LaBSEScorer(labse_model_dir, max_seq_len)

    lines = open(in_path, encoding="utf-8").readlines()
    print("# of lines:", len(lines))

    out_f = open(out_path, "w", encoding="utf-8")

    n = 0
    start = time.time()
    for i in range(0, len(lines), block):
        buf = lines[i:i+block]
        srcs = []
        tgts = []
        for line in buf:
            line = line.strip()
            pair = line.split("\t")
            src = pair[0]
            tgt = pair[1]
            srcs.append(src)
            tgts.append(tgt)

        ss = scorer.score(srcs, tgts)
        for j in range(len(ss)):
            out_f.write("{:.4f}\t{}\t{}\n".format(ss[j], srcs[j], tgts[j]))

        n += len(buf)
        if n % (40*block) == 0:
            t = time.time() - start
            print(n, n/t)

    print(n)
    out_f.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])