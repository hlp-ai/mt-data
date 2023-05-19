import sys

from yimt_bitext.web.sentence_vector import VectorSimilarityCosine, DummySentenceVectorization

if __name__ == "__main__":
    fn1 = sys.argv[1]
    fn2 = sys.argv[2]
    out = sys.argv[3]

    vec_scorer = VectorSimilarityCosine()
    dim = 32
    segment_vector = DummySentenceVectorization(dim)

    with open(fn1, encoding="utf-8") as f1, open(out, "w", encoding="utf-8") as of:
        for s in f1:
            s = s.strip()
            with open(fn2, encoding="utf-8") as f2:
                for t in f2:
                    t = t.strip()

                    v1 = segment_vector.get_vector(s)
                    v2 = segment_vector.get_vector(t)
                    score = vec_scorer.get_score(v1, v2)
                    of.write("{}\t{}\t{:.4f}\n".format(s, t, score))
