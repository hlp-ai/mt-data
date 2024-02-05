import sys
from collections import Counter

if __name__ == "__main__":
    corpus_fn = sys.argv[1]

    counter = Counter()
    total_lines = 0
    report_lines = 100000
    with open(corpus_fn, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            counter.update([c for c in line])

            total_lines += 1
            if total_lines % report_lines == 0:
                print(total_lines)
    print(total_lines)

    print("# of unique characters:", len(counter))
    print(counter.most_common(100))

    with open(corpus_fn+".char_counter", "w", encoding="utf-8") as f:
        for ch, n in counter.most_common(len(counter)):
            f.write(ch + "\n")
