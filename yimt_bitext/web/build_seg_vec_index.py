import argparse
from annoy import AnnoyIndex
from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2


def build_vec_index(sents_dir, segment_vector, annoy_dir=None, dim=768, tree_num=10):
    if annoy_dir is None:
        annoy_dir = sents_dir + ".vecindex"

    print("Building index {}".format(annoy_dir))

    vec_index = AnnoyIndex(dim, 'angular')
    block = 100  # 批处理行数
    segs = []
    i = 0
    j = 0
    with open(sents_dir, encoding="utf-8") as f:
        for s in f:
            segs.append(s.strip())
            i = i + 1
            if i % block == 0:  # 把句子集按block分批放入内存，进行句子嵌入向量，加入索引
                sentence_embeddings = segment_vector.get_vector(segs)
                segs = []
                for v in sentence_embeddings:
                    vec_index.add_item(j, v)
                    j = j + 1
                print(j)

    if len(segs) > 0:
        sentence_embeddings = segment_vector.get_vector(segs)  # 处理末尾小于block大小的句子集段
        for v in sentence_embeddings:
            vec_index.add_item(j, v)
            j = j + 1
        print(j)

    vec_index.build(tree_num)
    vec_index.save(annoy_dir)

    return annoy_dir


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file", required=True, help="Text file")
    argparser.add_argument("--annoy_dir", default=None, help="Annoy path for this language")
    argparser.add_argument("--dim", default=768, help="The dim of sentence embeddings")
    argparser.add_argument("--tree_num", default=10, help="The number of annoy trees")
    args = argparser.parse_args()

    fn = args.file
    annoy_dir = args.annoy_dir
    dim = args.dim
    tree_num = args.tree_num

    segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2",
                                                  "C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")

    build_vec_index(fn, segment_vector, annoy_dir, dim, tree_num)
