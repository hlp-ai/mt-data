import sys


if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path  = in_path + "-noscore"

    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        total  = 0
        for line in in_f:
            total += 1
            if total % 100000 == 0:
                print(total)
            line = line.strip()
            parts = line.split("\t")
            if len(parts) != 3:
                continue

            out_f.write(parts[1] + "\t" + parts[2] + "\n")

        print(total)