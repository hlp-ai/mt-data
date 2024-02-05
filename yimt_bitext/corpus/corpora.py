

class PairFromLine:
    """从文本行构建平行句子"""

    def __init__(self, sep_char="\t", positions=[0, 1]):
        self._sep_char = sep_char  # 列分割符号
        self._positions = positions  # 源和目标列位置

    def item(self, line):
        line = line.strip()
        if len(line) == 0:
            return None

        parts = line.split(self._sep_char)
        if len(parts) < 2:
            return None

        return parts[self._positions[0]], parts[self._positions[1]]


class SegmentFromLine:
    """从文本行构建句子"""

    def item(self, line):
        line = line.strip()
        if len(line) == 0:
            return None

        return line


class FileIterator:
    """从文本行文件构建语料库项迭代器"""

    def __init__(self, stream, get_item):
        self._stream = stream
        self._get_item = get_item

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = next(self._stream)

            e = self._get_item.item(line)
            if e is None:
                continue

            return e


class MapCorpus:
    """可随机访问语料，支持单语或平行语料"""

    def __init__(self, corpus_file, get_item):
        self._items = []

        with open(corpus_file, encoding="utf-8") as in_f:
            for line in in_f:
                e = get_item.item(line)
                if e is None:
                    continue

                self._items.append(e)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]


class IterableCorpus:
    """可迭代语料，支持单语或平行语料"""

    def __init__(self, corpus_file, get_item):
        self._in_f = open(corpus_file, encoding="utf-8")
        self._get_item = get_item

    def name(self):
        return "MapBiText"

    def __iter__(self):
        return FileIterator(self._in_f, self._get_item)

    def close(self):
        self._in_f.close()
