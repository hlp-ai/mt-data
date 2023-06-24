import argparse
from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2, SentenceVectorizationLaBSE


def build_vec_index(sentence_embeddings, annoy_dir, dim = 768, tree_num = 10):
    from annoy import AnnoyIndex
    t = AnnoyIndex(dim, 'angular')
    block = 100
    i = 0
    print("total sentence_embeddings:{}".format(len(sentence_embeddings)))
    for s in sentence_embeddings:
        t.add_item(i, s)
        i = i + 1
        if(i%block == 0):
            print("processed sentence_embeddings:{}".format(i))
    t.build(tree_num)
    t.save(annoy_dir)
    print("vec_index has been built successfully")


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

    sentence_embeddings = []
    block = 100
    t = 0
    for i in range(0, len(segs), block):
        b = segs[i:i + block]
        t += len(b)
        sentence_embeddings.extend(segment_vector.get_vector(b))
        print("embedded sentences: {}".format(t))
    print("all sentences have been embedded successfully")
    build_vec_index(sentence_embeddings, annoy_dir, dim, tree_num)


