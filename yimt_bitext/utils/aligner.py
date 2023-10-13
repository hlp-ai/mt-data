"""Sentence alignment based on LaBSE sentence embedding"""
from yimt_bitext.opus.bitext_scorers import LaBSEScorer


class SentenceEmbeddingAligner(object):
    """Sentence aligner based on LaBSE
    """

    def __init__(self, labse_dir="D:/kidden/mt/open/mt-ex/mt/data/labse1", max_len=48):
        self.match = {(1, 1): 0.9422141119221411,
                      (1, 2): 0.023114355231143552,
                      (2, 1): 0.0267639902676399,
                      (2, 2): 0.206082725060827251
                      }
        self.scorer = LaBSEScorer(labse_dir, max_len)

    def distance(self, partition1, partition2):
        """Distance between two sentence lists"""
        text1 = "".join(partition1)
        text2 = "".join(partition2)

        s = self.scorer.score([text1], [text2])[0]

        return -s

    def align(self, para1, para2):
        """Align sentences in two paragraphs

        Args:
            para1: list of sentences
            para2: list of sentences

        Returns:
            generator with type of aligned sentences tuple
        """
        align_trace = {}  # (cost, di, dj)
        for i in range(len(para1) + 1):
            for j in range(len(para2) + 1):
                if i == j == 0:
                    align_trace[0, 0] = (0, 0, 0)
                else:
                    align_trace[i, j] = (float('inf'), 0, 0)
                    for (di, dj), match_prob in self.match.items():  # for each match pattern
                        if i - di >= 0 and j - dj >= 0:
                            align_trace[i, j] = min(align_trace[i, j],
                                                    (
                                                        align_trace[i - di, j - dj][0] + self.distance(para1[i - di:i],
                                                                                                       para2[j - dj:j]),
                                                        di,  # number of sentences in lang1
                                                        dj))  # number of sentences in lang2

        i, j = len(para1), len(para2)
        while True:
            (c, di, dj) = align_trace[i, j]
            if di == dj == 0:  # reach the begining
                break
            # print(c)
            yield ''.join(para1[i - di:i]), ''.join(para2[j - dj:j])  # the aligned sentences
            i -= di
            j -= dj

    def align_paragraphs(self, paras1, paras2):
        pairs = []
        for sp, tp in zip(paras1, paras2):
            align = self.align(sp, tp)
            for a in align:
                pairs.append((a[0], a[1]))

        return pairs
