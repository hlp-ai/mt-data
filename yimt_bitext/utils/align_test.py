from yimt_bitext.utils.aligner import SentenceEmbeddingAligner

if __name__ == "__main__":
    aligner = SentenceEmbeddingAligner();

    p1 = ["Hi!", "what's your name?"]
    p2 = ["你好！", "你叫什么名字"]
    alen = aligner.align(p1, p2)
    for a in alen:
        print(a)
