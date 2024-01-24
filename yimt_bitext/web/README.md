# 基于CommonCrawl从Web中抽取平行语料
## 1. 获得给定CommonCrawl存档中的WET文档URL列表
```shell script
python yimt_bitext.web.get_wets_from_cc --cc_id <CommonCrawl ID> --out_dir <输出路径>
```
CommonCrawl存档ID例如CC-MAIN-2022-40

## 2. 下载和解析WET文档，输出每个链接的语言信息
```shell script
python yimt_bitext.web.dump_meta_from_wets --wet_paths_dir <WET列表文件所在目录> [--max_workers <下载线程数, 缺省1>]
```

## 3. 从语言信息元文件统计域名语言分布
```shell script
python yimt_bitxt.web.stat_from_meta --meta_dir <元文件路径>
```

## 4. 从统计文件中获得包括给定语言的多语站点
```shell script
python yimt_bitext.web.sites_from_stat --stat_file <统计数据文件路径> --langs <逗号分隔的3字母语言列表> [--out <结果文件路径>]
```