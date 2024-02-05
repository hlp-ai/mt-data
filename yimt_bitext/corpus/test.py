from yimt_bitext.corpus.corpora import IterableCorpus, MapCorpus, PairFromLine, SegmentFromLine

get_item_pair = PairFromLine(sep_char=" ")
bt1 = IterableCorpus("./c1.tsv", get_item_pair)
for p in bt1:
    print(p)
bt1.close()

print()

bt2 = MapCorpus("./c1.tsv", get_item_pair)
print(len(bt2))
for i in range(len(bt2)):
    print(bt2[i])

print()

get_item = SegmentFromLine()
bt1 = IterableCorpus("./c1.tsv", get_item)
for p in bt1:
    print(p)
bt1.close()

print()

bt2 = MapCorpus("./c1.tsv", get_item)
print(len(bt2))
for i in range(len(bt2)):
    print(bt2[i])