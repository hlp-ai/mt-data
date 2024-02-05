

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


def count_lines(fn):
    print("Counting lines...")
    lines = 0
    interval = 500000
    with open(fn, encoding="utf-8") as f:
        for _ in f:
            lines += 1
            if lines % interval == 0:
                print(lines)

    print(lines)

    return lines


def same_lines(path1, path2):
    """Two text files have the same numbers of lines?"""
    lines1 = 0
    lines2 = 0
    with open(path1, encoding="utf-8") as f:
        for _ in f:
            lines1 += 1

    with open(path2, encoding="utf-8") as f:
        for _ in f:
            lines2 += 1

    if lines1 == lines2:
        return True
    else:
        return False
