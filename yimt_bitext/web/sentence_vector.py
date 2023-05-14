import numpy as np


class SentenceVectorization:
    """计算文本或文本列表的向量表示"""

    def get_vector(self, text):
        raise NotImplementedError


class NaiveSentenceVectorization(SentenceVectorization):

    def get_vector(self, text):
        if text is str:
            return np.array([1.0, 2.0])
        elif text is list:
            return np.array([[1.0, 2.0], [1.0, 2.0]])


class SentenceVectorizationLaBSE(SentenceVectorization):
    def __init__(self, model_url, max_seq_length=48):
        self.max_seq_length = max_seq_length
        self.labse_model, labse_layer = self._get_model(model_url, max_seq_length)

        vocab_file = labse_layer.resolved_object.vocab_file.asset_path.numpy()
        do_lower_case = labse_layer.resolved_object.do_lower_case.numpy()

        import bert
        self.tokenizer = bert.bert_tokenization.FullTokenizer(vocab_file, do_lower_case)

    def _get_model(self, model_url, max_seq_length):
        import tensorflow as tf
        import tensorflow_hub as hub

        labse_layer = hub.KerasLayer(model_url, trainable=False)

        input_word_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_word_ids")
        input_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_mask")
        segment_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="segment_ids")

        # LaBSE layer.
        pooled_output, _ = labse_layer([input_word_ids, input_mask, segment_ids])

        # The embedding is l2 normalized.
        pooled_output = tf.keras.layers.Lambda(lambda x: tf.nn.l2_normalize(x, axis=1))(pooled_output)

        # Define model.
        return tf.keras.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=pooled_output), labse_layer

    def _create_input(self, input_strings, tokenizer, max_seq_length):
        input_ids_all, input_mask_all, segment_ids_all = [], [], []
        for input_string in input_strings:
            # Tokenize input.
            input_tokens = ["[CLS]"] + tokenizer.tokenize(input_string) + ["[SEP]"]
            input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
            sequence_length = min(len(input_ids), max_seq_length)

            # Padding or truncation.
            if len(input_ids) >= max_seq_length:
                input_ids = input_ids[:max_seq_length]
            else:
                input_ids = input_ids + [0] * (max_seq_length - len(input_ids))

            input_mask = [1] * sequence_length + [0] * (max_seq_length - sequence_length)

            input_ids_all.append(input_ids)
            input_mask_all.append(input_mask)
            segment_ids_all.append([0] * max_seq_length)

        return np.array(input_ids_all), np.array(input_mask_all), np.array(segment_ids_all)

    def get_vector(self, text):
        #输出句子的嵌入向量
        input_ids, input_mask, segment_ids = self._create_input(text, self.tokenizer, self.max_seq_length)
        return self.labse_model([input_ids, input_mask, segment_ids])


class VectorSimilarity:
    """计算向量或向量列表间的相似性分数"""

    def get_score(self, vec1, vec2):
        raise NotImplementedError


class NaiveVectorSimilarity(VectorSimilarity):

    def get_score(self, vec1, vec2):
        if len(vec1.shape) == 1 and len(vec2.shape) == 1:
            return 1.0
        elif len(vec1.shape) == 2 and len(vec2.shape) == 2:
            return [1.0, 1.0]


class VectorSimilarityCosine(VectorSimilarity):

    def get_score(self, vec1, vec2):     # 求向量余弦相似度
        num = float(np.dot(vec1, vec2))  # 向量点乘
        denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)  # 求模长的乘积
        return num / denom


class VectorSimilarityMargin(VectorSimilarity):
    #实现：边缘分数
    def __init__(self, index1, index2, k):
        #index1, index2是annoy索引树的索引，k是计算边缘分数式中的k值
        self.k = k
        self.index1 = index1
        self.index2 = index2
        self.cos_sim = VectorSimilarityCosine()

    def get_score(self, vec1, vec2):
        #计算np向量vec1, vec2之间的边缘分数
        cos_xy = self.cos_sim.get_score(vec1, vec2)
        src_neighbors = self.index1.get_nns_by_vector(vec1, self.k)
        tar_neighbors = self.index2.get_nns_by_vector(vec2, self.k)
        denominator = 0
        for v in src_neighbors:
            denominator += self.cos_sim.get_score(vec1, self.index1.get_item_vector(v))
        for v in tar_neighbors:
            denominator += self.cos_sim.get_score(vec2, self.index2.get_item_vector(v))
        denominator = denominator / self.k / 2
        margin = cos_xy / denominator
        return margin


def build_vec_index(sentence_embeddings, annoy_dir, dim=48, tree_num=10):
    #建立annoy索引树,num为树个数，load_dir为索引树存储路径
    from annoy import AnnoyIndex

    t = AnnoyIndex(dim, 'angular')
    i = 0
    for s in sentence_embeddings:
        t.add_item(i, s)
        i = i + 1
    t.build(tree_num)
    t.save(annoy_dir)


def load_vec_index(annoy_dir, dim=48):
    from annoy import AnnoyIndex

    vec_index = AnnoyIndex(dim, 'angular')
    vec_index.load(annoy_dir)

    return vec_index


if __name__ == '__main__':
    dim = 3
    src_embeddings = np.random.normal(0, 1, (100000, dim))
    tar_embeddings = np.random.normal(0, 1, (100000, dim))
    build_vec_index(src_embeddings, 'source.ann', dim, 6)
    build_vec_index(tar_embeddings, 'target.ann', dim, 6)

    vec_index1 = load_vec_index('source.ann', dim)
    vec_index2 = load_vec_index('target.ann', dim)

    k = 8
    get_margin = VectorSimilarityMargin(vec_index1, vec_index2, k)

    v1 = np.array([0, 3, 0])
    v2 = np.array([0, -3, 0])

    s=get_margin.get_score(v1,v2)
    print(s)