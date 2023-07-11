import numpy as np


class SentenceVectorization:
    """计算文本或文本列表的向量表示"""

    def get_vector(self, text):
        raise NotImplementedError

    def get_dim(self):
        raise NotImplementedError


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
        # text is a list
        input_ids, input_mask, segment_ids = self._create_input(text, self.tokenizer, self.max_seq_length)
        return self.labse_model([input_ids, input_mask, segment_ids])

    def get_dim(self):
        return 768


def normalize_vector(embeds):
    norms = np.linalg.norm(embeds, 2, axis=1, keepdims=True)
    return embeds / norms


class SentenceVectorizationLaBSE_2(SentenceVectorizationLaBSE):
    # 使用LaBSE_2和universal-sentence-encoder-cmlm/multilingual-preprocess_2嵌入句子

    def __init__(self, model_url,
                 preprocessor_url="https://hub.tensorflow.google.cn/google/universal-sentence-encoder-cmlm/multilingual-preprocess/2"):
        # preprocessor是tensorflow hub里的预处理器包，下载地址：https://tfhub.dev/google/universal-sentence-encoder-cmlm/multilingual-preprocess/2
        self.labse_model, self.preprocessor = self._get_model(model_url, preprocessor_url)

    def _get_model(self, model_url, preprocessor_url):
        import tensorflow_hub as hub
        import tensorflow_text  # 得有tensorflow_text，不然会报错
        labse_model = hub.KerasLayer(model_url)
        preprocessor = hub.KerasLayer(preprocessor_url)
        return labse_model, preprocessor

    def _create_input(self, input_strings):
        return self.preprocessor(input_strings)

    def get_vector(self, text):
        # text is a list
        input = self._create_input(text)
        return normalize_vector(self.labse_model(input)["default"])

    def get_dim(self):
        return 768


class VectorSimilarity:
    """计算向量或向量列表间的相似性分数"""

    def get_score(self, vec1, vec2):
        raise NotImplementedError


class VectorSimilarityCosine(VectorSimilarity):

    def get_score(self, vec1, vec2):
        # vec1 and vec2 with shape [b, d]
        sim = np.matmul(vec1, np.transpose(vec2))
        return sim


class VectorSimilarityMargin(VectorSimilarity):

    def __init__(self, index1, index2, k):
        # index1, index2是annoy索引树的索引，k是计算边缘分数式中的k值
        self.k = k
        self.index1 = index1
        self.index2 = index2
        self.cos_sim = VectorSimilarityCosine()

    def get_score(self, vec1, vec2):
        # 批计算np向量vec1, vec2之间的边缘分数，也兼容单个向量对计算
        vec1 = np.atleast_2d(vec1)
        vec2 = np.atleast_2d(vec2)

        cos_xy = self.cos_sim.get_score(vec1, vec2)

        margin = []
        for i in range(vec1.shape[0]):
            margin_in_row = []
            for j in range(vec2.shape[0]):
                src_neighbors = self.index1.get_nns_by_vector(vec1[i], self.k)
                tar_neighbors = self.index2.get_nns_by_vector(vec2[j], self.k)

                denominator = 0
                for v in src_neighbors:
                    denominator += self.cos_sim.get_score(vec1[i], self.index1.get_item_vector(v))
                for v in tar_neighbors:
                    denominator += self.cos_sim.get_score(vec2[j], self.index2.get_item_vector(v))
                denominator = denominator / self.k / 2
                margin_in_row.append(cos_xy[i][j] / denominator)

            margin.append(margin_in_row)

        return margin


def build_vec_index(sentence_embeddings, annoy_dir, dim=48, tree_num=10):
    # 建立annoy索引树,num为树个数，load_dir为索引树存储路径
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
    import tensorflow as tf

    s1 = ["This is a book", "I am a teacher."]
    t1 = ["这是一本书。", "我是老师。"]

    # vector = SentenceVectorizationLaBSE("D:/kidden/mt/open/mt-ex/mt/data/labse1")
    vector = SentenceVectorizationLaBSE_2(r"D:\kidden\mt\labse2", preprocessor_url=r"D:\kidden\mt\labse2\preprocess")
    v1 = vector.get_vector(s1)
    print(v1.shape)

    v2 = vector.get_vector(t1)
    print(v2.shape)

    scorer = VectorSimilarityCosine()
    s = scorer.get_score(v1, v2)
    print(s)
