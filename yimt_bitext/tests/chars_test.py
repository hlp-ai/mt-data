from yimt_bitext.utils.clean import is_whitespace

print(is_whitespace("\u3000"))
print(is_whitespace("\xa0"))
print(is_whitespace(" "))
print(is_whitespace("\t"))
print(is_whitespace("\n"))
print(is_whitespace("\r"))