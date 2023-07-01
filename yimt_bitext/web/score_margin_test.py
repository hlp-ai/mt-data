"""Test Margin_score sentence pairs"""

def score_tsv_margin(tsv_file, output_file, annoy_dir1, annoy_dir2, k = 8, dim = 768):
    from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2, load_vec_index, VectorSimilarityMargin
    segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2",
                                                  "C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")
    index1 = load_vec_index(annoy_dir1, dim)
    index2 = load_vec_index(annoy_dir2, dim)
    vec_scorer = VectorSimilarityMargin(index1, index2, k)

    block = 100  # 分批进行嵌入和评分，汇报进度
    i = 1
    src_segs = []
    tar_segs = []
    with open(tsv_file, encoding="utf-8") as f:
        with open(output_file, 'w') as of:
            # 用迭代器分行读写文件，解决文件过大的问题
            for s in f:
                src, tar = s.strip().split('\t')
                src_segs.append(src)
                tar_segs.append(tar)
                if (i % block == 0):
                    src_vec_segs = segment_vector.get_vector(src_segs)
                    tar_vec_segs = segment_vector.get_vector(tar_segs)
                    for j in range(block):
                        score = vec_scorer.get_score(src_vec_segs[j], tar_vec_segs[j])[0][0]
                        of.write("{:.6f} {} {}\n".format(score, src_segs[j], tar_segs[j]))
                    print("scored sentence pairs:{}".format(i))
                    src_segs = []
                    tar_segs = []
                i += 1
            src_vec_segs = segment_vector.get_vector(src_segs)
            tar_vec_segs = segment_vector.get_vector(tar_segs)
            for j in range(len(src_segs)):
                score = vec_scorer.get_score(src_vec_segs[j], tar_vec_segs[j])[0][0]
                of.write("{:.4f} {} {}\n".format(score, src_segs[j], tar_segs[j]))
            print("scored sentence pairs:{}".format(i-1))
    print("All sentence pairs have been scored successfully")

if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--tsv_file", required=True, help="Input file includes sentence pairs")
    argparser.add_argument("--output_file", required=True, help="Output file includes scores")
    argparser.add_argument("--annoy_dir1", required=True, help="Annoy path for language1")
    argparser.add_argument("--annoy_dir2", required=True, help="Annoy path for language2")
    argparser.add_argument("--k", default=8, help="The factor 'k' in margin formula")
    argparser.add_argument("--dim", default=768, help="The dim of sentence embeddings")
    args = argparser.parse_args()

    tsv_file = args.tsv_file
    output_file = args.output_file
    annoy_dir1 = args.annoy_dir1
    annoy_dir2 = args.annoy_dir2
    k = args.k
    dim = args.dim
    score_tsv_margin(tsv_file, output_file, annoy_dir1, annoy_dir2, k, dim)