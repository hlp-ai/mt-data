import argparse

def build_vec_index(sents_dir, annoy_dir, dim = 768, tree_num = 10):
    from annoy import AnnoyIndex
    from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2
    segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2",
                                                  "C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")
    t = AnnoyIndex(dim, 'angular')
    block = 100         # 批处理行数
    segs = []
    i = 0
    j = 0
    with open(sents_dir, encoding="utf-8") as f:     # 迭代器按行读取文本，而不是整个文本
        for s in f:
            segs.append(s.strip())
            i = i + 1
            if(i % block == 0):         # 把句子集按block分批放入内存，进行句子嵌入向量，加入索引
                sentence_embeddings = segment_vector.get_vector(segs)
                segs = []
                for v in sentence_embeddings:
                    t.add_item(j, v)
                    j = j + 1
                print("processed sentence_embeddings:{}".format(j))
    sentence_embeddings = segment_vector.get_vector(segs)     # 处理末尾小于block大小的句子集段
    for v in sentence_embeddings:
        t.add_item(j, v)
        j = j + 1
    print("processed sentence_embeddings:{}".format(j))
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

    build_vec_index(fn, annoy_dir, dim, tree_num)



