import sys

from yimt_bitext.filter import filter_score
from yimt_bitext.score import score_bitext


def process(raw_filter_path, min_score, model_path, block):
    path_s = raw_filter_path + ".score"
    path_sf = raw_filter_path + ".sfilter"

    print("Scoring {} into {}...".format(raw_filter_path, path_s))
    score_bitext.main(raw_filter_path, path_s, model_path, block)
    print()

    print("Filtering-by-socre {} into {}...".format(path_s, path_sf))
    filter_score.main(path_s, path_sf, min_score)
    print()


def main(pattern, start, end, model_path, min_score=0.70, block=16):
    for i in range(start, end):
        p = pattern.format(i)
        process(p, min_score, model_path, block)


if __name__ == "__main__":
    path_pattern = sys.argv[1]
    from_no = int(sys.argv[2])
    to_no = int(sys.argv[3])
    min_score = float(sys.argv[4])
    model_path = sys.argv[5]
    block = int(sys.argv[6])

    main(path_pattern, from_no, to_no, model_path, min_score, block)
