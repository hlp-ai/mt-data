from yimt_bitext.utils.normalizers import detok_zh_str

if __name__ == "__main__":
    print(detok_zh_str("AK 地区 需要 支付 额外 "))

    print(detok_zh_str("乐途 国际 青年 旅舍 "))

    print(detok_zh_str("Co Ngu Restaurant "))

    print(detok_zh_str("宫崎 县 国际 交流 协会 MIYAZAKI ."))

    print(detok_zh_str("博朗 Multiquick 手动 搅拌 "))

    print(detok_zh_str("Jwala Niketan Guesthouse 官 网 "))

    print(detok_zh_str("Jwala - Niketan Guest . house 官 网 "))
