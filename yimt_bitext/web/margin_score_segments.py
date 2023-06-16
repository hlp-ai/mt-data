"""6.2 Margin_score sentence pairs"""
import argparse

from yimt_bitext.web.sentence_vector import VectorSimilarityMargin, SentenceVectorizationLaBSE_2, load_vec_index, SentenceVectorizationLaBSE

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file1", required=True, help="Text file for language1")
    argparser.add_argument("--file2", required=True, help="Text file for language2")
    argparser.add_argument("--annoy_dir1", required=True, help="Annoy index for language1")
    argparser.add_argument("--annoy_dir2", required=True, help="Annoy Index for language2")
    # 本地向量检索文件路径

    argparser.add_argument("--k", default=8, help="The factor 'k' in margin formula")
    argparser.add_argument("--dim", default=768, help="The dim of sentence embeddings")
    # 这个向量维度dim默认768（这边测试使用的是labse_2）

    argparser.add_argument("--out", default=None, help="output file")
    args = argparser.parse_args()

    fn1 = args.file1
    fn2 = args.file2
    dim = args.dim
    k = args.k
    out = args.out

    index1 = load_vec_index(args.annoy_dir1, dim)
    index2 = load_vec_index(args.annoy_dir2, dim)

    vec_scorer = VectorSimilarityMargin(index1, index2, k)
    segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2","C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")
    # segment_vector = SentenceVectorizationLaBSE("D:/kidden/mt/open/mt-ex/mt/data/labse1")

    segs1 = []
    segs2 = []

    with open(fn1, encoding="utf-8") as f1:
        for s in f1:
            segs1.append(s.strip())

    n1 = len(segs1)

    with open(fn2, encoding="utf-8") as f2:
        for s in f2:
            segs2.append(s.strip())

    n2 = len(segs2)

    print("File-1: {}, File-2: {}".format(n1, n2))

    block = 16
    t1 = 0
    t2 = 0

    with open(out, "w", encoding="utf-8") as of:
        for i in range(0, len(segs1), block):
            b1 = segs1[i:i+block]
            t1 += len(b1)
            t2 = 0
            for j in range(0, len(segs2), block):
                b2 = segs2[j:j+block]
                v1 = segment_vector.get_vector(b1)
                v2 = segment_vector.get_vector(b2)
                scores = vec_scorer.get_score(v1, v2)
                for m, s in enumerate(b1, 0):
                    for n, t in enumerate(b2, 0):
                        of.write("{:.4f}\t{}\t{}\n".format(scores[m][n], s, t))   # 这里改用了list类型

                t2 += len(b2)
                print("File-1: {}, File-2: {}".format(t1, t2))