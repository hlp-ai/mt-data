import sys

from yimt_bitext.web.sentence_vector import DummySentenceVectorization


def build_vec_index(seg_vector, sentences, index_path, dim=48, tree_num=10):
    from annoy import AnnoyIndex

    t = AnnoyIndex(dim, 'angular')
    i = 0
    for s in sentences:
        s = s.strip()
        vec = seg_vector.get_vector(s)
        t.add_item(i, vec)
        i = i + 1
    t.build(tree_num)
    t.save(index_path)


if __name__ == "__main__":
    dim = 32
    segment_vector = DummySentenceVectorization(dim)
    text_fn = sys.argv[1]
    vec_index_path = sys.argv[2]

    with open(text_fn, encoding="utf-8") as f:
        build_vec_index(segment_vector, f, vec_index_path, dim=dim)