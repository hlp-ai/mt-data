from regex import regex

re_open_bracket = regex.compile(r"\p{Ps}")
re_close_bracket = regex.compile(r"\p{Pe}")

re_open_quote = regex.compile(r"\p{Pi}")
re_close_quote = regex.compile(r"\p{Pf}")


def is_open_bracket(c):
    return regex.match(re_open_bracket, c) is not None


def is_close_bracket(c):
    return regex.match(re_close_bracket, c) is not None


if __name__ == "__main__":
    print(is_open_bracket("<"))
    print(is_open_bracket("("))
    print(is_open_bracket("["))
    print(is_open_bracket("{"))
    print(is_open_bracket('"'))
    print(is_open_bracket("（"))
    print(is_open_bracket("《"))
    print(is_open_bracket("【"))
    print(is_open_bracket("”"))

    print()

    print(is_close_bracket(")"))
    print(is_close_bracket("】"))
