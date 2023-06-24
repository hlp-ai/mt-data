

EN_PUCTS = ",.?:;/<>()[]{}|\\~!@#$%^&*-+="


def is_en_punct(s):
    return len(s) == 1 and EN_PUCTS.find(s)>=0


def is_ascii_char(s):
    """Is it an ASCII char"""
    return len(s) == 1 and '\u0000' < s[0] < '\u00ff'


def is_basic_latin(s):
    return len(s) == 1 and '\u0000' < s[0] < '\u00ff'


def is_latin(s):
    return len(s) == 1 and '\u0000' < s[0] < '\u024f'
