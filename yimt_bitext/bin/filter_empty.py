import sys

if __name__ == "__main__":
    src_fn = sys.argv[1]
    tgt_fn = sys.argv[2]

    src_f = open(src_fn, encoding="utf-8")
    tgt_f = open(tgt_fn, encoding="utf-8")

    src_fn_f = src_fn + ".e"
    tgt_fn_f = tgt_fn + ".e"

    total = 0
    passed = 0

    with open(src_fn_f, "w", encoding="utf-8") as sf, open(tgt_fn_f, "w", encoding="utf-8") as tf:
        for src, tgt in zip(src_f, tgt_f):
            src = src.strip()
            tgt = tgt.strip()

            total += 1

            if total % 100000 == 0:
                print(total, passed)

            if len(src) > 0 and len(tgt) > 0:
                sf.write(src + "\n")
                tf.write(tgt + "\n")

                passed += 1

    print(total, passed)
