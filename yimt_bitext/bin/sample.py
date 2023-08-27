"""Sample some lines from corpus"""
import argparse
import io
import random

from opennmt.utils.misc import count_lines


def sample(files, n):
    """"Sample sentences from bitext or source and target file"""
    in_files = [io.open(f, encoding="utf-8") for f in files]
    out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]

    total = count_lines(files[0])
    print(total)

    sampled = 0
    scanned = 0
    sample_prob = (1.1*n) / total
    for p in zip(*in_files):
        scanned += 1
        prob = random.uniform(0, 1)
        if prob < sample_prob:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled % 10000 == 0:
                print(scanned, sampled)
            if sampled >= n:
                break
    print(scanned, sampled)

    for f in out_files:
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str, nargs="+", required=True, help="one or two files to be sampled")
    parser.add_argument("--num", type=int,required=True, help="the number of samples to be sampled")
    args = parser.parse_args()

    inputs = args.inputs
    sample_num = args.num

    if len(inputs) > 2:
        raise ValueError("Parallel corpus have at most two files.")

    sample(inputs, sample_num)
