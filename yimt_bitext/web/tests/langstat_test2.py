from yimt_bitext.web.base import LangStat

if __name__ == "__main__":
    lang2len = {"zh": 1000, "en": 20, "ko": 300}
    print(LangStat.languages(lang2len))
