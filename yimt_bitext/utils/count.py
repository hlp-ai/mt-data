

def count(fn, logger=None):
    total = 0
    empty = 0

    with open(fn, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            total += 1
            if len(line) == 0:
                empty += 1

            if total % 100000 == 0 and logger:
                logger.info("{}".format(total))

    if logger:
        logger.info("Total: {}, Empty: {}".format(total, empty))

    return total, empty
