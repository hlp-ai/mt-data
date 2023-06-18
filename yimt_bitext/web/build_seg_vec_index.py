import argparse
from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2, build_vec_index, SentenceVectorizationLaBSE

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file", required=True, help="Text file")
    argparser.add_argument("--annoy_dir", required=True, help="Annoy path for this language")
    argparser.add_argument("--dim", default=768, help="The dim of sentence embeddings")
    argparser.add_argument("--tree_num", default=10, help="The number of annoy trees")
    args = argparser.parse_args()

    fn = args.file
    annoy_dir = args.annoy_dir
    dim = args.dim
    tree_num = args.tree_num

    segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2",
                                                  "C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")
    # segment_vector = SentenceVectorizationLaBSE("D:/kidden/mt/open/mt-ex/mt/data/labse1")

    segs = []
    with open(fn, encoding="utf-8") as f:
        for s in f:
            segs.append(s.strip())
    n = len(segs)
    print("Text_file: {}".format(n))

    block = 100   # 句子集太大，分批进行嵌入和建立索引过程，报告进度
    t = 0
    for i in range(0, len(segs), block):
        b = segs[i:i + block]
        t += len(b)
        v = segment_vector.get_vector(b)
        build_vec_index(v, annoy_dir, dim, tree_num)
        print("Text_file: {}".format(t))

    print("Annoy index has been built successfully")

