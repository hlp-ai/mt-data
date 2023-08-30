import os
from argparse import ArgumentParser
from pathlib import Path

from yimt_bitext.utils.log import get_logger


def get_langs_from_dir(in_path):
    parts = Path(in_path).parts
    dn = parts[-1]
    langs = dn.split("-")
    sl, tl = langs
    return sl, tl


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--root", required=True, help="Root dir")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--clean", action="store_true", help="min socre for filtering")
    argparser.add_argument("--max_pairs", default=-1, type=int, help="max number of pairs for each corpus")
    argparser.add_argument("-se", "--sp_en_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.en-sp-32000.model",
                           help="EN sp model path")
    argparser.add_argument("-sz", "--sp_zh_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.zh.pretok-sp-32000.model",
                           help="ZH sp model path")
    argparser.add_argument("-m", "--ct2_zh_model",
                           default=r"D:\kidden\mt\mt-exp\en-zh\opus\ct2",
                           help="en-to-zh ct2 model path")
    argparser.add_argument("--log_dir", default="./", help="log directory")
    args = argparser.parse_args()

    logger_opus = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    preprocess_cmd = "python -m yimt_bitext.opus.preprocess --root {} --labse {} --block {} --min {} --max_pairs {} --clean"
    aug_cmd = "python -m yimt_bitext.bin.translate_aug --input {} --sp_en_model {} --sp_zh_model {} --ct2_zh_model {} --src_lang {} --clean"
    score_filter_cmd = "python -m yimt_bitext.bin.score_and_filter --input {} --labse {} --block {} --min {} --clean"

    root = args.root
    sub = os.listdir(root)
    contain_langs = all([os.path.isdir(os.path.join(root,d)) for d in sub])
    if not contain_langs:
        in_path = root
        sl, tl = get_langs_from_dir(in_path)

        os.popen(preprocess_cmd.format(in_path, args.labse, args.block, args.min, args.max_pairs)).readlines()

        out_path = os.path.join(root, "unzip", "tsv", "score", "sfilter", sl + "-" + tl + "-preprocessed.tsv")
        os.popen(aug_cmd.format(out_path, args.sp_en_model, args.sp_zh_model, args.ct2_zh_model, sl)).readlines()

        out_path = os.path.join(in_path, "unzip", "tsv", "score", "sfilter", "aug", sl + "-" + tl + "-preprocessed.tsv.2zh")
        os.popen(score_filter_cmd.format(out_path, args.labse, args.block, args.min)).readlines()
    else:
        for d in sub:
            in_path = os.path.join(root, d)
            sl, tl = get_langs_from_dir(in_path)

            os.popen(preprocess_cmd.format(root, args.labse, args.block, args.min, args.max_pairs)).readlines()

            out_path = os.path.join(in_path, "unzip", "tsv", "score", "sfilter", sl + "-" + tl + "-preprocessed.tsv")
            os.popen(aug_cmd.format(out_path, args.sp_en_model, args.sp_zh_model, args.ct2_zh_model, sl)).readlines()

            out_path = os.path.join(in_path, "unzip", "tsv", "score", "sfilter", "aug",
                                    sl + "-" + tl + "-preprocessed.tsv.2zh")
            os.popen(score_filter_cmd.format(out_path, args.labse, args.block, args.min)).readlines()