import regex


not_letter = regex.compile(r'[^\p{L}]')


def norm(s, lower=True, remove_noletter=True):
    if lower:
        s = s.lower()

    if remove_noletter:
        s = regex.sub(not_letter, "", s)
    return s


def dedup_file(in_path, out_path=None, logger=None):
    if out_path is None:
        out_path = in_path + ".deduped"
    pairs = set()

    n = 0
    total = 0

    with open(in_path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                if logger:
                    logger.info("Total: {}, Unique: {}".format(total, n))

            pn = norm(p)
            h = hash(pn)
            if h in pairs:
                logger.debug("Duplicate: {}".format(p))
                continue
            else:
                pairs.add(h)

            n += 1
            out_f.write(p + "\n")

    logger.info("Total: {}, Unique: {}".format(total, n))

    return out_path


if __name__ == "__main__":
    import sys
    in_fn = sys.argv[1]

    dedup_file(in_fn)