import time

from yimt_bitext.score.bitext_scorers import LaBSEScorer

if __name__ == "__main__":
    scorer = LaBSEScorer("D:/kidden/mt/open/mt-ex/mt/data/labse1", 72)

    english_sentences = ["dog", "Puppies are nice.", "I enjoy taking long walks along the beach with my dog."]
    chinese_sentences = ["狗", "小狗很好。", "我喜欢带着我的狗沿着海滩散步。"]

    start = time.time()
    print(scorer.score(english_sentences, chinese_sentences))
    print(time.time() - start)

