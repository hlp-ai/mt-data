import unicodedata


def is_whitespace(char):
    """Checks whether `chars` is a whitespace character."""
    # \t, \n, and \r are technically contorl characters but we treat them
    # as whitespace since they are generally considered as such.
    if char == " " or char == "\t" or char == "\n" or char == "\r":
        return True
    cat = unicodedata.category(char)
    if cat == "Zs":
        return True

    return False


def is_control(char):
    """Checks whether `chars` is a control character."""
    # These are technically control characters but we count them as whitespace
    # characters.
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    if cat in ("Cc", "Cf"):
        return True
    return False


def clean_text(text):
    """Performs invalid character removal and whitespace cleanup on text."""
    output = []
    for char in text:
        cp = ord(char)
        if cp == 0 or cp == 0xfffd or is_control(char):
            continue
        if is_whitespace(char):
            output.append(" ")
        else:
            output.append(char)
    return "".join(output)


def clean_file(in_path, out_path=None):
    if out_path is None:
        out_path = in_path + ".cleaned"

    n = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            line = line.strip()
            line = clean_text(line)
            out_f.write(line + "\n")

            n += 1

            if n % 1000 == 0:
                print(n)
    print(n)


if __name__ == "__main__":
    # print(clean_text("提⁠供⁠四⁠項⁠保⁠障⁠：房源預訂保障如果在罕見情況下，"))
    # print(clean_text("Last Updated: 2023 年 1 月 25 日Thank you for using Airbnb!"))
    # print(clean_text("�u���=:�����"))

    import sys

    in_fn = sys.argv[1]

    clean_file(in_fn)

