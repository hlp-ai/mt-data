from yimt_bitext.web.stat_from_meta import NetLangDist

if __name__ == "__main__":
    net2lang2len = NetLangDist("../../CC-MAIN-2022-40/domain2lang2len.json")
    print(len(net2lang2len))
    if "wikipedia.org" in net2lang2len:
        print(net2lang2len["wikipedia.org"])

    net2lang2len.update({"wikipedia.org":{"ara":10000}})
    print(net2lang2len["wikipedia.org"])

    for e in net2lang2len:
        print(e)

    for n, lang2len in net2lang2len.items():
        if len(lang2len) > 1:
            print(n, lang2len)
