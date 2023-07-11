import argparse
from yimt_bitext.opus.utils import pair_to_single
from yimt_bitext.web.build_seg_vec_index import build_vec_index
from yimt_bitext.web.sentence_vector import SentenceVectorizationLaBSE_2, load_vec_index, VectorSimilarityMargin, \
    SentenceVectorizationLaBSE


def build_vec_index_tsv(tsv_file, segment_vector, indexfile1=None, indexfile2=None, dim=768, tree_num=10):
    src_file = tsv_file + ".src"
    tar_file = tsv_file + ".tgt"

    print("Splitting {} into {} and {}".format(tsv_file, src_file, tar_file))
    pair_to_single(tsv_file, src_file, tar_file)

    index_path1 = build_vec_index(src_file, segment_vector, indexfile1, dim, tree_num)
    index_path2 = build_vec_index(tar_file, segment_vector, indexfile2, dim, tree_num)

    return index_path1, index_path2


def score_tsv_margin(tsv_file, output_file, segment_vector, annoy_dir1, annoy_dir2, k=8, dim=768):
    index1 = load_vec_index(annoy_dir1, dim)
    index2 = load_vec_index(annoy_dir2, dim)
    vec_scorer = VectorSimilarityMargin(index1, index2, k)

    block = 100  # 分批进行嵌入和评分，汇报进度
    i = 0
    src_segs = []
    tar_segs = []
    with open(tsv_file, encoding="utf-8") as f, open(output_file, 'w', encoding="utf-8") as of:
        for s in f:
            src, tar = s.strip().split('\t')
            src_segs.append(src)
            tar_segs.append(tar)
            i += 1
            if i % block == 0:
                src_vec_segs = segment_vector.get_vector(src_segs)
                tar_vec_segs = segment_vector.get_vector(tar_segs)
                for j in range(block):
                    score = vec_scorer.get_score(src_vec_segs[j], tar_vec_segs[j])[0][0]
                    of.write("{:.4f} {} {}\n".format(score, src_segs[j], tar_segs[j]))

                src_segs = []
                tar_segs = []
                print(i)

        if len(src_segs) > 0:
            src_vec_segs = segment_vector.get_vector(src_segs)
            tar_vec_segs = segment_vector.get_vector(tar_segs)
            for j in range(len(src_segs)):
                score = vec_scorer.get_score(src_vec_segs[j], tar_vec_segs[j])[0][0]
                of.write("{:.4f} {} {}\n".format(score, src_segs[j], tar_segs[j]))
            print(i)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--tsv_file", required=True, help="Input tsv file")
    argparser.add_argument("--output", default=None, help="Output file with scores")
    args = argparser.parse_args()

    tsv_file = args.tsv_file
    output_file = args.output

    # segment_vector = SentenceVectorizationLaBSE_2("D:/LaBSE_2",
    #                                               "C:/Users/Lenovo/Desktop/universal-sentence-encoder-cmlm_multilingual-preprocess_2")
    segment_vector = SentenceVectorizationLaBSE("D:/kidden/mt/open/mt-ex/mt/data/labse1")

    index_path1, index_path2 = build_vec_index_tsv(tsv_file, segment_vector)

    if output_file is None:
        output_file = tsv_file + ".score"
    score_tsv_margin(tsv_file, output_file, segment_vector, index_path1, index_path2)
