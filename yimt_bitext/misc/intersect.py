import sys

from yimt_bitext.normalize.normalizers import norm


def intersect(tsv_file1, tsv_file2, out_file, creterion="SRC",
             lower=True, remove_noletter=True):
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0
    print("Scanning file1...")
    with open(tsv_file1, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 10000 == 0:
                print(total)
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    print(total)

    intersected = 0
    total = 0

    print("Scanning file2...")
    with open(tsv_file2, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Intersected:", intersected)

            if creterion == "SRC" or creterion == "TGT":
                pp = p.split("\t")
                if len(pp) != 2:
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if creterion == "SRC":
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs in srcs:
                        out_f.write(p + "\n")
                        intersected += 1
                else:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht in tgts:
                        out_f.write(p + "\n")
                        intersected += 1
            else:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h in pairs:
                    out_f.write(p + "\n")
                    intersected += 1

    print("Total:", total, "Intersected:", intersected)


if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    out = sys.argv[3]

    intersect(f1, f2, out, "SRCTGT")