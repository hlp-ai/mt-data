"""Interface for core concepts"""
import json
import os
import langid
import sqlite3

from yimt_bitext.utils.lang import detect_lang
from yimt_bitext.web.web import URL


class WetParser:

    def __init__(self, wet_file):
        self.wet_file = wet_file

    def parse(self):
        """Generator of parsed result

        :return: dict of parsed result
        """
        pass


class LangID:

    def detect(self, text):
        pass


class BasicLangID(LangID):

    def detect(self, text):
        return detect_lang(text)


class SentenceSplitter:

    def split(self, text):
        pass


class BasicSentenceSplitter(SentenceSplitter):

    def split(self, text):
        paragraphs = text.split("\n")
        paragraphs = [p.strip() for p in paragraphs]
        paragraphs = list(filter(lambda p: len(p)>0, paragraphs))

        return paragraphs


def get_domain(host):
    u = URL(host)
    domain = u.fld
    return domain


class LangStat:

    def update(self, host, lang2len):
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
        """domain list"""
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
    def languages(cls, lang2len):
        total_langs = len(lang2len.keys())
        total_lens = sum(lang2len.values())
        avg_len = total_lens / total_langs
        ret = []
        for lang in lang2len.keys():
            if lang2len[lang] > avg_len/5:
                ret.append(lang)

        return ret


def merge_lang2len(old_lang2len, new_lang2len):
    for lang, length in new_lang2len.items():
        if lang not in old_lang2len:
            old_lang2len[lang] = length
        else:
            old_lang2len[lang] += length

    return old_lang2len


class BasicLangStat(LangStat):

    def __init__(self, stat_file):
        self.stat_file = stat_file
        if os.path.exists(self.stat_file):
            print("Loading stat from", self.stat_file)
            with open(stat_file, encoding="utf-8") as stream:
                self.stat = json.load(stream)
        else:
            self.stat = {}

    def update(self, host, lang2len):
        domain = get_domain(host)
        if domain not in self.stat:
            self.stat[domain] = {host: lang2len}
        else:
            host2lang2len = self.stat[domain]
            if host not in host2lang2len:
                host2lang2len[host] = lang2len
            else:
                old_lang2len = host2lang2len[host]
                merge_lang2len(old_lang2len, lang2len)

    def stat_by_domain(self, domain):
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
        for domain in self.domains():
            lang2len = self.lang2len_by_domain(domain)
            langs_in_domain = self.languages(lang2len)
            found = True
            for lang in langs:
                if lang not in langs_in_domain:
                    found = False
                    break
            if found:
                yield domain

    def hosts_for_langs(self, langs):
        for domain in self.domains_for_langs(langs):
            hosts = []
            host2lang2len = self.stat_by_domain(domain)
            for host, lang2len in host2lang2len.items():
                for lang in langs:
                    if lang in lang2len.keys():
                        hosts.append(host)
                        break
            yield domain, hosts

class SqliteLangStat(LangStat):
    def __init__(self, db_file):
        self.db_file=db_file
        if os.path.exists(self.db_file):
            print("connecting", self.db_file)
            self.con = sqlite3.connect(db_file)
            self.cur=self.con.cursor()
        else:
            self.con = sqlite3.connect('%s'%db_file)
            self.cur = self.con.cursor()
            self.cur.execute("CREATE TABLE language(\
                       host CHAR NOT NULL,\
                       domain CHAR NOT NULL,\
                       lang CHAR NOT NULL,\
                       lang2len INT,\
                       primary key(host,lang));")
            self.con.commit()

    def update(self, host, lang2len):
        for key in lang2len:
            self.cur.execute("SELECT host,lang From language WHERE host='%s' AND lang ='%s'"\
                             %(host,key))
            f=self.cur.fetchone()
            if f:
                self.cur.execute("UPDATE language SET lang2len = lang2len+%d WHERE host = '%s' AND lang ='%s';" \
                                 % (lang2len[key],host, key))
                self.con.commit()
            else:
                domain = get_domain(host)
                self.cur.execute("INSERT INTO language VALUES ('%s','%s','%s','%d')"\
                                 %(host,domain,key,lang2len[key]))
                self.con.commit()

    def stat_by_domain(self, domain):
        self.cur.execute("SELECT host,lang,lang2len From language WHERE domain ='%s'" \
                         % (domain))
        f = self.cur.fetchall()
        if f:
            statdomain = {}
            statdomain[domain]={}
            for a in f:
                domain_lang2len={a[1]:a[2]}
                if a[0] not in statdomain[domain]:
                    statdomain[domain][a[0]]=domain_lang2len
                else:
                    merge_lang2len(statdomain[domain][a[0]],domain_lang2len)
            return statdomain[domain]
        else:
            return None

    def stat_by_host(self, host):
        domain = get_domain(host)
        self.cur.execute("SELECT host,domain,lang,lang2len From language WHERE host ='%s'" \
                         % (host))
        f = self.cur.fetchall()
        if f:
            stathost = {}
            stathost[domain] = {}
            for a in f:
                domain_lang2len={a[2]:a[3]}
                if a[0] not in stathost[domain]:
                    stathost[domain][a[0]]=domain_lang2len
                else:
                    merge_lang2len(stathost[domain][a[0]],domain_lang2len)
            return stathost[domain][host]
        else:
            return None

    def lang2len_by_domain(self, domain):
        host2lang2len = self.stat_by_domain(domain)
        if host2lang2len is None:
            return None
        lang2len_ret = {}
        for host, lang2len in host2lang2len.items():
            lang2len_ret = merge_lang2len(lang2len_ret, lang2len)
        return lang2len_ret

    def domains(self):
        self.cur.execute("SELECT domain From language")
        f = self.cur.fetchall()
        domainslist={}
        for a in f:
            if a[0] not in domainslist:
                domainslist[a[0]]={}
        return domainslist.keys()

    def hosts(self, domain):
        self.cur.execute("SELECT host From language WHERE domain = '%s'"%domain)
        f = self.cur.fetchall()
        hostslist={}
        for a in f:
            if a[0] not in hostslist:
                hostslist[a[0]]={}
        return hostslist.keys()

    def size(self):
        return len(self.domains())

    def save(self):
        self.cur.close()
        self.con.close()

    def domains_for_langs(self, langs):
        for domain in self.domains():
            lang2len = self.lang2len_by_domain(domain)
            langs_in_domain = self.languages(lang2len)
            found = True
            for lang in langs:
                if lang not in langs_in_domain:
                    found = False
                    break
            if found:
                yield domain

    def hosts_for_langs(self, langs):
        for domain in self.domains_for_langs(langs):
            hosts = []
            host2lang2len = self.stat_by_domain(domain)
            for host, lang2len in host2lang2len.items():
                for lang in langs:
                    if lang in lang2len.keys():
                        hosts.append(host)
                        break
            yield domain, hosts

class SentenceRepo:

    def store(self, sentences):
        pass


class BasicSentenceRepo(SentenceRepo):

    def __init__(self, path="./"):
        self.path = path
        self.repo = {}

    def store(self, lang2sentences):
        for lang, sents in lang2sentences.items():
            if lang not in self.repo:
                self.repo[lang] = []
            self.repo[lang] += sents

    def __str__(self):
        description= "# of sentences extracted for languages: "
        for lang, sents in self.repo.items():
            description += lang + ": " + str(len(sents)) + "; "
        return description


class SentenceRepoFile(SentenceRepo):

    def __init__(self, path="./lang2sents", accepted_langs=None):
        self.path = path
        self.lang2f = {}
        self.lang2len = {}
        self.accepted_langs = accepted_langs

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        else:
            lang_files = os.listdir(path)
            for f in lang_files:
                if f.endswith(".txt"):
                    lang = f[0:f.find(".txt")]
                    with open(os.path.join(path, f), encoding="utf-8") as stream:
                        self.lang2len[lang] = len(stream.readlines())
                    self.lang2f[lang] = open(os.path.join(self.path, f), "a", encoding="utf-8")

    def store(self, lang2sentences):
        for lang, sents in lang2sentences.items():
            if self.accepted_langs is not None and lang not in self.accepted_langs:
                continue
            if lang not in self.lang2f:
                self.lang2f[lang] = open(os.path.join(self.path, lang + ".txt"), "a", encoding="utf-8")
                self.lang2len[lang] = 0
            count = self.lang2len[lang]
            for s in sents:
                self.lang2f[lang].write(s + "\n")
                count += 1
                if count % 50 == 0:
                    self.lang2f[lang].flush()
            self.lang2len[lang] += len(sents)

    def __str__(self):
        description= "# of sentences extracted for languages: "
        for lang, count in self.lang2len.items():
            description += lang + ": " + str(count) + "; "
        return description
