from yimt_bitext.web.dump_meta_from_wets import iter_metadata_wet


wet_path = r"D:\dataset\cc\CC-MAIN-2022-49\CC-MAIN-20221126080725-20221126110725-00002.warc.wet"

for url, site, domain, lang, content_len in iter_metadata_wet(wet_path):
    print(url, site, domain, lang, content_len)