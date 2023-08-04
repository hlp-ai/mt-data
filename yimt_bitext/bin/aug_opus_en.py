import os
from argparse import ArgumentParser
from pathlib import Path

from yimt_bitext.bin.score_and_filter import score_and_filter
from yimt_bitext.bin.translate_aug import aug_from_en
from yimt_bitext.opus.preprocess import preprocess_dir
from yimt_bitext.utils.log import get_logger


def run_preprocess(in_dir,
                   labse_model_dir,
                   block,
                   min_score,
                   clean_after_done,
                   max,
                   logger_dir,
                   queue):
    logger = get_logger(os.path.join(logger_dir, "opus.log"), "OPUS")
    en_preprocessed_file = preprocess_dir(in_dir, labse_model_dir, block, min_score,
                                          clean_after_done, max, logger)
    queue.put(en_preprocessed_file)


def  run_aug(en_preprocessed_file, sp_en_model, sp_zh_model, ct2_zh_model, sl, clean, logger_dir, queue):
    logger = get_logger(os.path.join(logger_dir, "opus.log"), "OPUS")
    en_translated_file = aug_from_en(en_preprocessed_file, sp_en_model, sp_zh_model, ct2_zh_model, sl,
                                     clean, logger)
    queue.put(en_translated_file)


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--input", required=True, help="input dir")
    argparser.add_argument("--labse", default="D:/kidden/mt/open/mt-ex/mt/data/labse1", help="directory for labse")
    argparser.add_argument("--block", type=int, default=8, help="block size for labse")
    argparser.add_argument("--min", type=float, default=0.6, help="min socre for filtering")
    argparser.add_argument("--clean", action="store_true", help="clean after processing")
    argparser.add_argument("--max_pairs", default=-1, type=int, help="max number of pairs for each corpus")
    argparser.add_argument("--log_dir", default="./", help="log directory")

    argparser.add_argument("-se", "--sp_en_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.en-sp-32000.model",
                           help="EN sp model path")
    argparser.add_argument("-sz", "--sp_zh_model",
                           default=r"D:\kidden\mt\mt-exp\sp\opus-enzh-all-sf.zh.pretok-sp-32000.model",
                           help="ZH sp model path")
    argparser.add_argument("-m", "--ct2_zh_model",
                           default=r"D:\kidden\mt\mt-exp\en-zh\opus\ct2",
                           help="en-to-zh ct2 model path")

    args = argparser.parse_args()

    logger = get_logger(os.path.join(args.log_dir, "opus.log"), "OPUS")

    import multiprocessing

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_preprocess, args=(args.input, args.labse, args.block, args.min,
                   args.clean, args.max_pairs, args.log_dir, queue,))
    p.start()
    p.join()
    en_preprocessed_file = queue.get()

    # en_preprocessed_file = preprocess_dir(args.input, labse_model_dir=args.labse, block=args.block, min_score=args.min,
    #                clean_after_done=args.clean, max=args.max_pairs, logger=logger)

    parts = Path(args.input).parts
    dirname = parts[-1]
    langs = dirname.split("-")
    if len(langs) == 2:
        sl, tl = langs
        target_lang = tl
    else:
        logger.warn("No language pair exist: {}".format(dirname))
        exit(-1)

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_aug, args=(en_preprocessed_file, args.sp_en_model, args.sp_zh_model, args.ct2_zh_model,
                                                      sl, args.clean, args.log_dir, queue,))
    p.start()
    p.join()
    en_translated_file = queue.get()

    # en_translated_file = aug_from_en(en_preprocessed_file, args.sp_en_model, args.sp_zh_model, args.ct2_zh_model, sl, args.clean, logger)

    score_and_filter(en_translated_file, labse_model_dir=args.labse, block=args.block, min_socre=args.min,
                     clean_after_done=args.clean, logger=logger)
