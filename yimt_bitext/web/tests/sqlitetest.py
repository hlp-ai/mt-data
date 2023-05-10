from yimt_bitext.web.base import SqliteLangStat

if __name__ == "__main__":
    stat_f = "./123.db"
    lang_stat = SqliteLangStat(stat_f)

    lang_stat.update("http://www.abc.com/", {"zh": 100, "en": 30})
    lang_stat.update("http://en.abc.com/", {"en": 100})

    assert lang_stat.size() == 1
    assert len(lang_stat.hosts("abc.com")) == 2

    lang_stat.save()

    lang_stat = SqliteLangStat(stat_f)
    lang2len = lang_stat.lang2len_by_domain("abc.com")
    assert lang2len["en"] == 130
    lang2len = lang_stat.lang2len_by_host("http://en.abc.com/")
    assert lang2len["en"] == 100

    hosts = list(lang_stat.hosts_for_langs(["en", "zh"]))
    assert len(hosts) == 2
