import json
import os

from yimt_bitext.web.web import URL


class LangStat:

    def update(self, host, lang2len):
        """更新主机下语言分布数据"""
        pass

    def stat_by_domain(self, domain):
        """host2lang2len for the given domain"""
        pass

    def stat_by_host(self, host):
        """lang2len for the given host"""
        pass

    def lang2len_by_domain(self, domain):
        """lang2len for the given domain"""
        pass

    def lang2len_by_host(self, host):
        return self.stat_by_host(host)

    def domains(self):
        """所有域名列表"""
        pass

    def hosts(self, domain):
        """the host list in the domain"""
        pass

    def size(self):
        """number of domains"""
        pass

    def save(self):
        pass

    def domains_for_langs(self, langs):
        pass

    def hosts_for_langs(self, langs):
        pass

    @classmethod
    def languages(cls, lang2len, ratio=5.0):
        """从语言分布信息返回可能的多语语言列表"""
        total_langs = len(lang2len.keys())
        total_lens = sum(lang2len.values())
        avg_len = total_lens / total_langs  # 每个语言的平均长度
        ret = []
        for lang in lang2len.keys():
            if lang2len[lang] > avg_len / ratio:
                ret.append(lang)

        return ret


def merge_lang2len(old_lang2len, new_lang2len):
    """合并两个语言分布信息"""
    for lang, length in new_lang2len.items():
        if lang not in old_lang2len:
            old_lang2len[lang] = length
        else:
            old_lang2len[lang] += length

    return old_lang2len


def get_domain(host):
    u = URL(host)
    domain = u.fld
    return domain


class BasicLangStat(LangStat):

    def __init__(self, stat_file):
        self.stat_file = stat_file
        if os.path.exists(self.stat_file):
            print("Loading stat from", self.stat_file)
            with open(stat_file, encoding="utf-8") as stream:
                self.stat = json.load(stream)
            print("# of domains:", len(self.stat))
        else:
            self.stat = {}

    def update(self, host, lang2len):
        """更新主机下语言分布数据"""
        domain = get_domain(host)
        if domain not in self.stat:  # 新域名
            self.stat[domain] = {host: lang2len}
        else:
            host2lang2len = self.stat[domain]
            if host not in host2lang2len:  # 新主机
                host2lang2len[host] = lang2len
            else:
                old_lang2len = host2lang2len[host]
                merge_lang2len(old_lang2len, lang2len)

    def stat_by_domain(self, domain):
        """获得给定域名下每个主机的语言分布"""
        if domain not in self.stat:
            return None
        else:
            return self.stat[domain]

    def stat_by_host(self, host):
        domain = get_domain(host)
        if domain not in self.stat:
            return None
        else:
            host2lang2len = self.stat[domain]
            if host not in host2lang2len:
                return None
            else:
                return host2lang2len[host]

    def lang2len_by_domain(self, domain):
        """获得给定域名下的语言分布"""
        host2lang2len = self.stat_by_domain(domain)
        if host2lang2len is None:
            return None

        lang2len_ret = {}
        for host, lang2len in host2lang2len.items():
            lang2len_ret = merge_lang2len(lang2len_ret, lang2len)

        return lang2len_ret

    def domains(self):
        return self.stat.keys()

    def hosts(self, domain):
        if domain not in self.stat:
            return None

        return self.stat[domain].keys()

    def size(self):
        return len(self.stat)

    def save(self):
        with open(self.stat_file, "w", encoding="utf-8") as stream:
            json.dump(self.stat, stream)

    def domains_for_langs(self, langs):
        """获得包含给定语言列表的多语域名"""
        for domain in self.domains():
            lang2len = self.lang2len_by_domain(domain)
            langs_in_domain = self.languages(lang2len)  # 可能的多语语言
            found = True
            for lang in langs:
                if lang not in langs_in_domain:
                    found = False
                    break
            if found:
                yield domain

    def hosts_for_langs(self, langs):
        """获得包含给定语言列表之一语言的host"""
        for domain in self.domains_for_langs(langs):  # 对包含语言列表的多语域名
            hosts = []
            host2lang2len = self.stat_by_domain(domain)
            for host, lang2len in host2lang2len.items():
                # TODO: 根据语言的文本长度比例确定主机是否包括语言
                for lang in langs:
                    if lang in lang2len.keys():  # 主机包含语言之一
                        hosts.append(host)
                        break
            yield domain, hosts
