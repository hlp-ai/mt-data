"""合并一个目录下的文件到一个文件"""
import argparse
import os

# from yimt_bitext.opus.utils import get_files
from yimt_bitext.utils.log import get_logger


def get_files(source):
    if isinstance(source, list):
        data_files = []
        for f in source:
            if os.path.isfile(f):
                data_files.append(f)
            else:
                files = [os.path.join(f, sf) for sf in os.listdir(f)]
                data_files.extend(files)
        return data_files
    elif os.path.isdir(source):
        data_files = [os.path.join(source, f) for f in os.listdir(source)]
        return data_files
    else:
        return source


def merge(source, out_fn, clean_after_merge=False, max=-1, logger_opus=None):
    data_files = get_files(source)

    out_path = out_fn
    if os.path.exists(out_path):
        logger_opus.info("{} exits".format(out_path))
        return out_path

    data_files = list(filter(lambda f: os.path.isfile(f), data_files))
    if len(data_files) == 0:
        logger_opus.info("No file to merge")
        return out_path

    out_path = merge_files(data_files, out_path, clean_after_merge=clean_after_merge, max=max, logger_opus=logger_opus)

    return out_path


def merge_files(data_files, out_path, clean_after_merge=False, max=-1, logger_opus=None):
    """Merge files into one file"""
    total = 0
    with open(out_path, "w", encoding="utf-8") as out_f:
        for f in data_files:
            cnt = 0
            with open(f, encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if len(line) > 0:
                        out_f.write(line + "\n")
                        total += 1
                        cnt += 1
                        if total % 100000 == 0:
                            if logger_opus:
                                logger_opus.info("Merging {} into {}: {}/{}".format(f, out_path, cnt, total))
                        if 0 < max <= total:
                            if logger_opus:
                                logger_opus.info("Merged {}, reach max".format(total))
                            break

            if logger_opus:
                logger_opus.info("Merged {} into {}: {}/{}".format(f, out_path, cnt, total))

        if logger_opus:
            logger_opus.info("Merged {}: {}".format(out_path, total))

    if clean_after_merge:
        for f in data_files:
            os.remove(f)

    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True, help="input files or directories")
    parser.add_argument("-o", "--output", required=True, help="output file")
    parser.add_argument("--log_dir", default="./", help="log directory")
    args = parser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    merge(args.input, args.output, logger_opus=logger_opus)
