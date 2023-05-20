import sys

from yimt_bitext.web.sentence_vector import VectorSimilarityCosine, SentenceVectorizationLaBSE

if __name__ == "__main__":
    fn1 = sys.argv[1]
    fn2 = sys.argv[2]
    out = sys.argv[3]

    vec_scorer = VectorSimilarityCosine()
    segment_vector = SentenceVectorizationLaBSE("D:/kidden/mt/open/mt-ex/mt/data/labse1")

    segs1 = []
    segs2 = []

    with open(fn1, encoding="utf-8") as f1:
        for s in f1:
            segs1.append(s.strip())

    with open(fn2, encoding="utf-8") as f2:
        for s in f2:
            segs2.append(s.strip())

    block = 16

    with open(out, "w", encoding="utf-8") as of:
        for i in range(0, len(segs1), block):
            b1 = segs1[i:i+block]
            for j in range(0, len(segs2), block):
                b2 = segs2[j:j+block]

                v1 = segment_vector.get_vector(b1)
                v2 = segment_vector.get_vector(b2)
                scores = vec_scorer.get_score(v1, v2)

                for m, s in enumerate(b1, 0):
                    for n, t in enumerate(b2, 0):
                        of.write("{:.4f} {} {}\n".format(scores[m, n], s, t))
