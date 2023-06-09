import hashlib


def get_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    t1 = "what can i do for you? this is just a test."
    h = get_hash(t1)
    print(len(h), h, hash(t1))
