from yimt_bitext.normalize.normalizers import Cleaner

cleaner = Cleaner()
print(cleaner.normalize("a  bc\tthis is a test."))
print(cleaner.normalize("\u0001 a bc\t this ia中文"))
