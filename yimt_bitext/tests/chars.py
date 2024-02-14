

def is_ascii(c):
    return len(c) == 1 and '\u0000' <= c <= '\u00FF'


def is_ascii_print(c):
    return len(c) == 1 and '\u0020' <= c <= '\u007E'


print(is_ascii("a"), is_ascii_print("a"))


def print_unicode(start, stop, width=30):
    for code in range(start, stop):
        end = '\n' if (code-start)%width==0 else ' '
        print(chr(code), end=end)


print_unicode(128000, 128300)


import unicodedata
for c in range(128000, 128100):
    print(chr(c), unicodedata.name(chr(c)))

