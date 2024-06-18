from yimt_bitext.normalize.normalizers import Cleaner, HTMLEntityUnescape

cleaner = Cleaner()
print(cleaner.normalize("a  bc\tthis is a test."))
print(cleaner.normalize("\u0001 a bc\t this ia中文"))

unescape = HTMLEntityUnescape(True, True)
p = "i like&nbsp;\t&nbsp do."
print(unescape.normalize(p))
