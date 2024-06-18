from yimt_bitext.normalize.normalizers import load_normalizers

if __name__ == "__main__":
    cs = load_normalizers("../utils/normalizers.yml")
    print(cs)

    text = "how   are you\t我 喜欢 book ."
    for c in cs:
        text = c.normalize(text)
    print(text)