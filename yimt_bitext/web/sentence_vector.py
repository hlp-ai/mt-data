import numpy as np


class SentenceVectorization:

    def get_vector(self, text):
        raise NotImplementedError


class NaiveSentenceVectorization(SentenceVectorization):

    def get_vector(self, text):
        if text is str:
            return np.array([1.0, 2.0])
        elif text is list:
            return np.array([[1.0, 2.0], [1.0, 2.0]])


class SentenceVectorizationLaBSE(SentenceVectorization):

    def get_vector(self, text):
        pass


class VectorSimilarity:

    def get_score(self, vec1, vec2):
        raise NotImplementedError


class NaiveVectorSimilarity(VectorSimilarity):

    def get_score(self, vec1, vec2):
        if len(vec1.shape) == 1 and len(vec2.shape) == 1:
            return 1.0
        elif len(vec1.shape) == 2 and len(vec2.shape) == 2:
            return [1.0, 1.0]


class VectorSimilarityCosine(VectorSimilarity):

    def get_score(self, vec1, vec2):
        pass


class VectorSimilarityMargin(VectorSimilarity):

    def get_score(self, vec1, vec2):
        pass
