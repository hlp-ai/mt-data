import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from functools import partial

from yimt_bitext.bin import score_and_filter
from yimt_bitext.bin.hant2hans import hant2s_file
from yimt_bitext.gui.win_utils import ask_open_file, ask_save_file, ask_dir
from yimt_bitext.opus.utils import pair_to_single, single_to_pair, extract_zips, merge_moses, merge, split, \
    score_and_filter_pattern, diff
from yimt_bitext.utils.count import count
from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.filters import filter_file, EmptyFilter, SameFilter, OverlapFilter, RepetitionFilter, \
    NonZeroNumeralsFilter, AlphabetRatioFilter, get_lang2script, CharacterRatioFilter, LengthFilter
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import normalize_file, ToZhNormalizer, CleanerTSV
from yimt_bitext.utils.tokenization import tokenize_single, detok_zh

logger_opus = get_logger("./opus.log", "CORPUS")


def create_unzip_corpus(parent):
    tk.Label(parent, text="Input Directory").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output Directory (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_output = tk.Entry(parent, width=50)
    entry_corpus_output.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_output)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_datapath = entry_corpus_datapath.get().strip()
        unzip_dir = entry_corpus_output.get().strip()
        if len(unzip_dir) == 0:
            unzip_dir = None

        if len(corpus_datapath) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus directory empty.")
            return

        extract_zips(corpus_datapath, unzip_dir, logger_opus=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Unzip Files", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_merge_moses_corpus(parent):
    tk.Label(parent, text="Input directory").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_datapath = tk.Entry(parent, width=50)
    entry_mergemoses_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_mergemoses_datapath)).grid(row=0, column=2,
                                                                                                  padx=10, pady=5)

    tk.Label(parent, text="Output directory(Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_outpath = tk.Entry(parent, width=50)
    entry_mergemoses_outpath.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_mergemoses_outpath)).grid(row=1, column=2, padx=10,
                                                                                             pady=5)

    tk.Label(parent, text="Source language").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_sl = tk.Entry(parent, width=50)
    entry_mergemoses_sl.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(parent, text="Target language").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_tl = tk.Entry(parent, width=50)
    entry_mergemoses_tl.grid(row=3, column=1, padx=10, pady=5)

    def go():
        corpus_mergemoses_datapath = entry_mergemoses_datapath.get().strip()
        corpus_output_path = entry_mergemoses_outpath.get().strip()
        if len(corpus_output_path) == 0:
            corpus_output_path = None
        corpus_mergemoses_sl = entry_mergemoses_sl.get().strip()
        if len(corpus_mergemoses_sl) == 0:
            corpus_mergemoses_sl = None
        corpus_mergemoses_tl = entry_mergemoses_tl.get().strip()
        if len(corpus_mergemoses_tl) == 0:
            corpus_mergemoses_tl = None

        merge_moses(corpus_mergemoses_datapath, corpus_mergemoses_sl, corpus_mergemoses_tl, corpus_output_path,
                    logger_opus=logger_opus)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Merge Moses Files", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_merge_corpus(parent):
    tk.Label(parent, text="Input Directory").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_tgt)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_datapath = entry_corpus_datapath.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_datapath) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        merge(corpus_datapath, corpus_tgt, logger_opus=logger_opus)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Merge Files into One File", command=go).grid(row=5, column=1,
                                                                                        padx=10, pady=5)


def create_normalize_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_in = tk.Entry(parent, width=50)
    entry_normalize_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_normalize_in)).grid(row=0, column=2,
                                                                                                 padx=10, pady=5)

    tk.Label(parent, text="Output File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_out = tk.Entry(parent, width=50)
    entry_normalize_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_normalize_out)).grid(row=1, column=2,
                                                                                                  padx=10,
                                                                                                  pady=5)

    tk.Label(parent, text="About Chinese").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_zh = tk.Entry(parent, width=50)
    entry_zh.grid(row=2, column=1, padx=10, pady=5)
    entry_zh.insert(0, "tozh")

    def go():
        corpus_normalize_in = entry_normalize_in.get().strip()
        corpus_normalize_out = entry_normalize_out.get().strip()
        if len(corpus_normalize_out) == 0:
            corpus_normalize_out = corpus_normalize_in + ".normalized"

        zh = entry_zh.get().strip()

        if len(corpus_normalize_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        if zh == "tozh":
            normalizers = [ToZhNormalizer()]
        else:
            normalizers = [CleanerTSV()]

        normalize_file(corpus_normalize_in, normalizers, out_path=corpus_normalize_out, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Normalize Bitext", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_dedup_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_in = tk.Entry(parent, width=50)
    entry_dedup_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_dedup_in)).grid(row=0, column=2,
                                                                                             padx=10, pady=5)

    tk.Label(parent, text="Output file (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_out = tk.Entry(parent, width=50)
    entry_dedup_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_dedup_out)).grid(row=1, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Dedup Condition").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    var_srctgt = IntVar()
    check_srctgt = Checkbutton(parent, text="Source and Target", variable=var_srctgt, onvalue=1, offvalue=0)
    check_srctgt.grid(row=2, column=1, padx=10, pady=5)
    check_srctgt.select()

    var_src = IntVar()
    check_src = Checkbutton(parent, text="Source", variable=var_src, onvalue=1, offvalue=0)
    check_src.grid(row=3, column=1, padx=10, pady=5)

    var_tgt = IntVar()
    check_tgt = Checkbutton(parent, text="Target", variable=var_tgt, onvalue=1, offvalue=0)
    check_tgt.grid(row=4, column=1, padx=10, pady=5)

    var_noletter = IntVar()
    check_noletter = Checkbutton(parent, text="No Letter", variable=var_noletter, onvalue=1, offvalue=0)
    check_noletter.grid(row=5, column=1, padx=10, pady=5)
    check_noletter.select()

    def go():
        corpus_dedup_in = entry_dedup_in.get().strip()
        corpus_dedup_out = entry_dedup_out.get().strip()

        if len(corpus_dedup_out) == 0:
            corpus_dedup_out = corpus_dedup_in + ".deduped"

        if len(corpus_dedup_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        dedup_srctgt = True if var_srctgt.get() == 1 else False
        dedup_src = True if var_src.get() == 1 else False
        dedup_tgt = True if var_tgt.get() == 1 else False
        no_letter = True if var_noletter.get() == 1 else False

        dedup_bitext_file(corpus_dedup_in, corpus_dedup_out,
                          dedup_srctgt=dedup_srctgt, dedup_src=dedup_src, dedup_tgt=dedup_tgt,
                          remove_noletter=no_letter,
                          logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Dedup Bitext", command=go).grid(row=6, column=1, padx=10, pady=5)


def create_diff_corpus(parent):
    tk.Label(parent, text="Input TSV file1").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_base = tk.Entry(parent, width=50)
    entry_dedup_base.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_dedup_base)).grid(row=0, column=2,
                                                                                             padx=10, pady=5)
    tk.Label(parent, text="Input TSV file2").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_in = tk.Entry(parent, width=50)
    entry_dedup_in.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_dedup_in)).grid(row=1, column=2,
                                                                                             padx=10, pady=5)

    tk.Label(parent, text="Output file (Optional)").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_out = tk.Entry(parent, width=50)
    entry_dedup_out.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_dedup_out)).grid(row=2, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Diff Condition").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_cond = tk.Entry(parent, width=50)
    entry_cond.grid(row=3, column=1, padx=10, pady=5)
    entry_cond.insert(0, "SRC")

    def go():
        corpus_dedup_base = entry_dedup_base.get().strip()
        corpus_dedup_in = entry_dedup_in.get().strip()
        corpus_dedup_out = entry_dedup_out.get().strip()
        diff_cond = entry_cond.get().strip()

        if len(corpus_dedup_out) == 0:
            corpus_dedup_out = None

        if len(corpus_dedup_in) == 0 or len(corpus_dedup_base)==0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        diff(corpus_dedup_base, corpus_dedup_in, corpus_dedup_out, creterion=diff_cond, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="C1-C2", command=go).grid(row=4, column=1, padx=10, pady=5)


def create_filter_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_filter_in = tk.Entry(parent, width=50)
    entry_filter_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_filter_in)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output file (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_filter_out = tk.Entry(parent, width=50)
    entry_filter_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_filter_out)).grid(row=1, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="Language Pair").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_filter_langpair = tk.Entry(parent, width=50)
    entry_filter_langpair.grid(row=2, column=1, padx=10, pady=5)
    entry_filter_langpair.insert(0, "en-zh")

    def go():
        corpus_filter_in = entry_filter_in.get().strip()
        corpus_filter_out = entry_filter_out.get().strip()
        corpus_filter_langpair = entry_filter_langpair.get().strip()

        if len(corpus_filter_out) == 0:
            corpus_filter_out = corpus_filter_in + ".filtered"

        if len(corpus_filter_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        filters = [EmptyFilter(), SameFilter(), OverlapFilter(ratio=0.80), NonZeroNumeralsFilter(threshold=1.0),
                   AlphabetRatioFilter(threshold=0.33, exclude_whitespace=True), RepetitionFilter()]

        lang2script = get_lang2script()

        lang_pair = corpus_filter_langpair
        sl, tl = lang_pair.split("-")
        src_script = lang2script[sl]
        tgt_script = lang2script[tl]
        char_filter = CharacterRatioFilter(scripts=(src_script, tgt_script), thresholds=(0.33, 0.33))
        filters.append(char_filter)

        if tl == "en":
            tgt_len = LengthFilter.space_sep_len_f
            filters.append(LengthFilter(tgt_len_fn=tgt_len, tgt_lens=(1, 128)))

        filter_file(corpus_filter_in, filters=filters, out_path=corpus_filter_out, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Filter Bitext", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_split_corpus(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_split_in1 = tk.Entry(parent, width=50)
    entry_split_in1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_split_in1)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Number of Samples in each File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_split_number = tk.Entry(parent, width=50)
    entry_split_number.grid(row=1, column=1, padx=10, pady=5)
    entry_split_number.insert(0, "100000")

    def go():
        corpus_split_in1 = entry_split_in1.get().strip()
        corpus_split_number = entry_split_number.get().strip()

        if len(corpus_split_number) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        split(corpus_split_in1, int(corpus_split_number))

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Split Corpus Equally", command=go).grid(row=2, column=1, padx=10, pady=5)


def create_score_filter_corpus(parent):
    tk.Label(parent, text="Input TSV file pattern").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_filter_in = tk.Entry(parent, width=50)
    entry_filter_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_filter_in)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="# of start").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_filter_start = tk.Entry(parent, width=50)
    entry_filter_start.grid(row=1, column=1, padx=10, pady=5)
    entry_filter_start.insert(0, "0")

    tk.Label(parent, text="# of end").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_filter_end = tk.Entry(parent, width=50)
    entry_filter_end.grid(row=2, column=1, padx=10, pady=5)
    entry_filter_end.insert(0, "1")

    tk.Label(parent, text="Min score").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_filter_min = tk.Entry(parent, width=50)
    entry_filter_min.grid(row=3, column=1, padx=10, pady=5)
    entry_filter_min.insert(0, "0.70")

    tk.Label(parent, text="Path of LaBSE model").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=4, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_model)).grid(row=4, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Size of block").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_filter_block = tk.Entry(parent, width=50)
    entry_filter_block.grid(row=5, column=1, padx=10, pady=5)
    entry_filter_block.insert(0, "16")

    def go():
        corpus_filter_in = entry_filter_in.get().strip()
        corpus_model = entry_model.get().strip()

        if len(corpus_filter_in) == 0 or len(corpus_model) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        start = int(entry_filter_start.get().strip())
        end = int(entry_filter_end.get().strip())
        block = int(entry_filter_block.get().strip())
        min_score = float(entry_filter_min.get().strip())

        score_and_filter_pattern(corpus_filter_in, start, end, corpus_model, min_score, block, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Score and Filter bitext", command=go).grid(row=6, column=1, padx=10, pady=5)


def create_tsv2mono_corpus(parent):
    tk.Label(parent, text="TSV File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_pair = tk.Entry(parent, width=50)
    entry_corpus_pair.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_pair)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Source File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_src = tk.Entry(parent, width=50)
    entry_corpus_src.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_src)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    tk.Label(parent, text="Target File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_tgt)).grid(row=2, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        pair_to_single(corpus_pair, corpus_src, corpus_tgt)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="TSV to Mono", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_mono2tsv_corpus(parent):
    tk.Label(parent, text="Source File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_src = tk.Entry(parent, width=50)
    entry_corpus_src.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_src)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="Target File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_tgt)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    tk.Label(parent, text="TSV File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_pair = tk.Entry(parent, width=50)
    entry_corpus_pair.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_pair)).grid(row=2, column=2,
                                                                                                padx=10,
                                                                                                pady=5)

    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        single_to_pair(corpus_src, corpus_tgt, corpus_pair)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Mono to TSV", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_han2hans_corpus(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_han2hans_in = tk.Entry(parent, width=50)
    entry_han2hans_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_han2hans_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_han2hans_out = tk.Entry(parent, width=50)
    entry_han2hans_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_han2hans_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_han2hans_in = entry_han2hans_in.get().strip()
        corpus_han2hans_out = entry_han2hans_out.get().strip()
        if len(corpus_han2hans_in) == 0 or len(corpus_han2hans_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        hant2s_file(corpus_han2hans_in, corpus_han2hans_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Hant2Hans", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_sample_corpus(parent):
    tk.Label(parent, text="TSV File/Source File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in1 = tk.Entry(parent, width=50)
    entry_sample_in1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in1)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="Target File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in2 = tk.Entry(parent, width=50)
    entry_sample_in2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in2)).grid(row=1, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="number of samples").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_sample_number = tk.Entry(parent, width=50)
    entry_sample_number.grid(row=2, column=1, padx=10, pady=5)

    def go():
        corpus_sample_in1 = entry_sample_in1.get().strip()
        corpus_sample_in2 = entry_sample_in2.get().strip()
        corpus_sample_number = entry_sample_number.get().strip()
        if len(corpus_sample_in1) != 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in1, corpus_sample_in2]
        elif len(corpus_sample_in1) != 0 and len(corpus_sample_in2) == 0:
            files = [corpus_sample_in1]
        elif len(corpus_sample_in1) == 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in2]
        else:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        if len(corpus_sample_number) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        sample(files, int(corpus_sample_number))
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Sample sentences into a new corpus", command=go).grid( \
        row=5, column=1, padx=10, pady=5)


def create_partition_corpus(parent):
    tk.Label(parent, text="TSV File/Source File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in1 = tk.Entry(parent, width=50)
    entry_sample_in1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in1)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="Target File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in2 = tk.Entry(parent, width=50)
    entry_sample_in2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in2)).grid(row=1, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="number of samples").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_sample_number = tk.Entry(parent, width=50)
    entry_sample_number.grid(row=2, column=1, padx=10, pady=5)

    def go():
        corpus_sample_in1 = entry_sample_in1.get().strip()
        corpus_sample_in2 = entry_sample_in2.get().strip()
        corpus_sample_number = entry_sample_number.get().strip()
        if len(corpus_sample_in1) != 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in1, corpus_sample_in2]
        elif len(corpus_sample_in1) != 0 and len(corpus_sample_in2) == 0:
            files = [corpus_sample_in1]
        elif len(corpus_sample_in1) == 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in2]
        else:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        if len(corpus_sample_number) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        partition(files, int(corpus_sample_number))
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Partition a corpus into two copora", command=go).grid( \
        row=5, column=1, padx=10, pady=5)


def create_tok_mono(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_in = tk.Entry(parent, width=50)
    entry_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_out = tk.Entry(parent, width=50)
    entry_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    tk.Label(parent, text="Input Language").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_lang = tk.Entry(parent, width=50)
    entry_lang.grid(row=2, column=1, padx=10, pady=5)
    entry_lang.insert(0, "zh")

    def go():
        corpus_in = entry_in.get().strip()
        corpus_out = entry_out.get().strip()
        if len(corpus_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        if len(corpus_out) == 0:
            corpus_out = None

        lang = entry_lang.get().strip()
        tokenize_single(corpus_in, lang, corpus_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Tokenize File", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_detok_zh(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_in = tk.Entry(parent, width=50)
    entry_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_out = tk.Entry(parent, width=50)
    entry_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_in = entry_in.get().strip()
        corpus_out = entry_out.get().strip()
        if len(corpus_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        if len(corpus_out) == 0:
            corpus_out = None

        detok_zh(corpus_in, corpus_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Detokenize Chinese Text", command=go).grid(row=2, column=1, padx=10, pady=5)


def create_count(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    def go():
        corpus_datapath = entry_corpus_datapath.get().strip()

        if len(corpus_datapath) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus File empty.")
            return

        count(corpus_datapath, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Count Lines", command=go).grid(row=1, column=1, padx=10, pady=5)