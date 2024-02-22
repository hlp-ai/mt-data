"""将域名meta记录进行分组"""
import glob
import os
import shutil
from argparse import ArgumentParser

BUCKET_NUM = 67  # 域名组数
BASE = 13
FLUSH_INTERVAL = 150  # 扫描多少个meta文件刷新写出一次


def hash_domain(domain):
    s = 0
    for c in domain:
        s += BASE * ord(c)

    return s % BUCKET_NUM


def flush_meta(records, group_dir, g_id):
    if len(records) == 0:
        return

    g_dir = os.path.join(group_dir, "{}".format(g_id))

    meta_files = glob.glob(os.path.join(g_dir, "*.meta"))
    f_no = 0
    if len(meta_files) > 0:
        fnos = list(sorted([int(os.path.basename(mf).split(".")[0]) for mf in meta_files]))
        f_no = fnos[-1] + 1

    g_file = os.path.join(g_dir, "{}.meta".format(f_no))

    print("Flushing", g_file)

    with open(g_file, "w", encoding="utf-8") as out:
        for line in records:
            out.write(line + "\n")


def group_meta(meta_dir, group_dir):
    grouped_meta_dir = os.path.join(meta_dir, "grouped_meta")
    if not os.path.exists(grouped_meta_dir):
        os.mkdir(grouped_meta_dir)

    meta_files = glob.glob(os.path.join(meta_dir, "*.meta"))
    if len(meta_files) == 0:
        print("No meta file to process.")
        return

    groups = []
    for _ in range(BUCKET_NUM):
        groups.append([])

    total = len(meta_files)
    done = 0
    for idx, meta_file in enumerate(meta_files):
        print("Grouping metadata file {}: {}/{}".format(meta_file, done, total))

        with open(meta_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                parts = line.split()
                url, host, domain, lang, content_len = parts
                g_id = hash_domain(domain)

                groups[g_id].append(line)

        done += 1
        if done % FLUSH_INTERVAL == 0:
            for i in range(len(groups)):
                flush_meta(groups[i], group_dir, i)

            groups = []
            for _ in range(BUCKET_NUM):
                groups.append([])

        shutil.move(meta_file, grouped_meta_dir)

    for i in range(len(groups)):
        flush_meta(groups[i], group_dir, i)


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    argparser.add_argument("--group_dir", default=None, help="Directory of group metadata file")
    args = argparser.parse_args()

    meta_dir = args.meta_dir
    group_dir = args.group_dir

    if group_dir is None:
        group_dir = os.path.join(meta_dir, "group_meta")

    if not os.path.exists(group_dir):
        print("Create dir", group_dir)
        os.makedirs(group_dir, exist_ok=True)

    for i in range(BUCKET_NUM):
        g_dir = os.path.join(group_dir, "{}".format(i))
        if not os.path.exists(g_dir):
            print("Create dir", g_dir)
            os.makedirs(g_dir, exist_ok=True)

    group_meta(meta_dir, group_dir)
