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


class SentenceRepo:

    def store(self, lang2sentences):
        pass

    def sizes(self):
        pass

    def flush(self):
        pass

    def close(self):
        self.flush()


class BasicSentenceRepo(SentenceRepo):

    def __init__(self, path="./lang2sents"):
        self.path = path
        self.repo = {}

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        else:
            lang_files = os.listdir(path)
            for f in lang_files:
                if f.endswith(".txt"):
                    lang = f[0:f.find(".txt")]
                    sentences = set()
                    with open(os.path.join(path, f), encoding="utf-8") as stream:
                        for line in stream:
                            line = line.strip()
                            sentences.add(line)
                    self.repo[lang] = sentences


    def store(self, lang2sentences):
        for lang, sents in lang2sentences.items():
            if lang not in self.repo:
                self.repo[lang] = set()
            self.repo[lang].update(sents)

    def __str__(self):
        description= "# of sentences extracted for languages: "
        for lang, sents in self.repo.items():
            description += lang + ": " + str(len(sents)) + "; "
        return description

    def flush(self):
        for lang, sents in self.repo.items():
            with open(os.path.join(self.path, lang + ".txt"), "w", encoding="utf-8") as f:
                for s in sents:
                    f.write(s + "\n")

    def sizes(self):
        counts = [(len(sents), lang) for lang, sents in self.repo.items()]
        counts = list(sorted(counts))

        return counts



class SentenceRepoFile(SentenceRepo):

    def __init__(self, path="./lang2sents", save_interval=50):
        self.path = path
        self.lang2f = {}
        self.lang2len = {}
        self._save_interval = save_interval

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
            if lang not in self.lang2f:
                self.lang2f[lang] = open(os.path.join(self.path, lang + ".txt"), "a", encoding="utf-8")
                self.lang2len[lang] = 0
            count = self.lang2len[lang]
            for s in sents:
                self.lang2f[lang].write(s + "\n")
                count += 1
                if count % self._save_interval == 0:
                    self.lang2f[lang].flush()
            self.lang2len[lang] += len(sents)

    def __str__(self):
        description= "# of sentences extracted for languages: "
        for lang, count in self.lang2len.items():
            description += lang + ": " + str(count) + "; "
        return description

    def sizes(self):
        counts = [(count, lang) for lang, count in self.lang2len.items()]
        counts = list(sorted(counts))

        return counts
