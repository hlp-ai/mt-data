import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from functools import partial

from yimt_bitext.bin.remove_scores import strip_scores
from yimt_bitext.bin.sample import sample
from yimt_bitext.utils.sp import train_spm, load_spm, tokenize_file, detokenize_file

from yimt_bitext.bin.hant2hans import hant2s_file
from yimt_bitext.gui.win_utils import ask_open_file, ask_save_file, ask_dir
from yimt_bitext.opus.utils import pair_to_single, single_to_pair, extract_zips, merge, split, \
    score_and_filter_pattern, diff, merge_moses_only, intersect, partition
from yimt_bitext.utils.count import count
from yimt_bitext.utils.dedup import dedup_bitext_file
from yimt_bitext.utils.filters import filter_file, load_filters
from yimt_bitext.utils.log import get_logger
from yimt_bitext.utils.normalizers import normalize_file, load_normalizers
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

        merge_moses_only(corpus_mergemoses_datapath, corpus_mergemoses_sl, corpus_mergemoses_tl, corpus_output_path,
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
    tk.Label(parent, text="Input TSV File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
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

    tk.Label(parent, text="Normalizers Conf File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_conf = tk.Entry(parent, width=50)
    entry_normalize_conf.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_normalize_conf)).grid(row=2, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_normalize_in = entry_normalize_in.get().strip()
        corpus_normalize_out = entry_normalize_out.get().strip()
        if len(corpus_normalize_out) == 0:
            corpus_normalize_out = corpus_normalize_in + ".normalized"

        conf = entry_normalize_conf.get().strip()

        if len(corpus_normalize_in) == 0 or len(conf)==0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        normalizers = load_normalizers(conf)

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

    var_noletter = IntVar()
    check_noletter = Checkbutton(parent, text="No Letter", variable=var_noletter, onvalue=1, offvalue=0)
    check_noletter.grid(row=4, column=1, padx=10, pady=5)
    check_noletter.select()

    def go():
        corpus_dedup_base = entry_dedup_base.get().strip()
        corpus_dedup_in = entry_dedup_in.get().strip()
        corpus_dedup_out = entry_dedup_out.get().strip()
        diff_cond = entry_cond.get().strip()

        no_letter = True if var_noletter.get() == 1 else False

        if len(corpus_dedup_out) == 0:
            corpus_dedup_out = None

        if len(corpus_dedup_in) == 0 or len(corpus_dedup_base)==0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        diff(corpus_dedup_base, corpus_dedup_in, corpus_dedup_out, creterion=diff_cond,
             remove_noletter=no_letter, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="C1-C2", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_intersect_corpus(parent):
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

    tk.Label(parent, text="Output file").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_out = tk.Entry(parent, width=50)
    entry_dedup_out.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_dedup_out)).grid(row=2, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Intersection Condition").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_cond = tk.Entry(parent, width=50)
    entry_cond.grid(row=3, column=1, padx=10, pady=5)
    entry_cond.insert(0, "SRCTGT")

    var_noletter = IntVar()
    check_noletter = Checkbutton(parent, text="No Letter", variable=var_noletter, onvalue=1, offvalue=0)
    check_noletter.grid(row=4, column=1, padx=10, pady=5)
    check_noletter.select()

    def go():
        corpus_dedup_base = entry_dedup_base.get().strip()
        corpus_dedup_in = entry_dedup_in.get().strip()
        corpus_dedup_out = entry_dedup_out.get().strip()
        cond = entry_cond.get().strip()

        no_letter = True if var_noletter.get() == 1 else False

        if len(corpus_dedup_in) == 0 or len(corpus_dedup_base)==0 or len(corpus_dedup_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        intersect(corpus_dedup_base, corpus_dedup_in, corpus_dedup_out, creterion=cond,
             remove_noletter=no_letter, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="C1&C2", command=go).grid(row=5, column=1, padx=10, pady=5)


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

    tk.Label(parent, text="Filters Conf File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_filter_conf = tk.Entry(parent, width=50)
    entry_filter_conf.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_filter_conf)).grid(row=2, column=2,
                                                                                                   padx=10, pady=5)

    def go():
        corpus_filter_in = entry_filter_in.get().strip()
        corpus_filter_out = entry_filter_out.get().strip()
        corpus_filter_conf = entry_filter_conf.get().strip()

        if len(corpus_filter_out) == 0:
            corpus_filter_out = corpus_filter_in + ".filtered"

        if len(corpus_filter_in) == 0 or len(corpus_filter_conf)==0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        filters = load_filters(corpus_filter_conf)

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

    tk.Label(parent, text="Number of samples").grid(row=2, column=0, padx=10, pady=5, sticky="e")
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


def get_file_name(p):
    return os.path.basename(p)


def get_sp_prefix(corpus_path, vocab_size):
    corpus_path = get_file_name(corpus_path)
    return "{}-sp-{}".format(corpus_path, vocab_size)


def get_tok_file(corpus_path):
    corpus_path = get_file_name(corpus_path)
    return corpus_path + ".tok"


def get_detok_file(corpus_path):
    corpus_path = get_file_name(corpus_path)
    return corpus_path + ".detok"


def create_sp_train(parent):
    tk.Label(parent, text="Raw Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Size of vocab").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_vocab_size.insert(0, "4800")

    tk.Label(parent, text="SP model path").grid(row=2, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_model)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(parent, text="Max num of sentences (M)").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_max_sentences = tk.Entry(parent)
    entry_max_sentences.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entry_max_sentences.insert(0, "5")

    tk.Label(parent, text="Character coverage").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_coverage = tk.Entry(parent)
    entry_coverage.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entry_coverage.insert(0, "0.9999")

    tk.Label(parent, text="User Defined Symbols File").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_symbols_file = tk.Entry(parent, width=50)
    entry_symbols_file.grid(row=5, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_symbols_file)).grid(row=5, column=2, padx=10,
                                                                                           pady=5)

    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        vocab_size = entry_vocab_size.get()
        if len(vocab_size.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab size empty.")
            return

        sp_model = entry_model.get()
        if len(sp_model.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Model path empty.")
            return

        sp_model = os.path.join(sp_model, get_sp_prefix(corpus_file, vocab_size))

        print(corpus_file, vocab_size, sp_model)

        max_sents = int(float(entry_max_sentences.get()) * 1000000)

        symbols_file = entry_symbols_file.get()
        if len(symbols_file.strip()) == 0:
            symbols_file = None

        train_spm(corpus_file, sp_model, vocab_size,
                  num_sentences=max_sents,
                  coverage=entry_coverage.get(),
                  user_defined_symbols_file=symbols_file)

        tk.messagebox.showinfo(title="Info", message="SentencePiece model created.")

    tk.Button(parent, text="Train SentencePiece Model", command=go).grid(row=6, column=1, padx=10, pady=5)


def create_sp_tokenize(parent):
    tk.Label(parent, text="Raw Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(parent, text="...", command=partial(ask_open_file, entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="SP model path").grid(row=1, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry_model)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output path").grid(row=2, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=2, column=2, padx=10, pady=5)


    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        sp_model = entry_model.get()
        if len(sp_model.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="SP model empty.")
            return

        tok_output = entry_output.get()
        if len(tok_output.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Output path empty.")
            return

        tok_output = os.path.join(tok_output, get_tok_file(corpus_file))

        print(corpus_file, sp_model, tok_output)

        sp = load_spm(sp_model)
        tokenize_file(sp, corpus_file, tok_output)

        tk.messagebox.showinfo(title="Info", message="Raw corpus tokenized.")

    tk.Button(parent, text="Tokenize Corpus with SP", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_sp_detokenize(parent):
    tk.Label(parent, text="Tokenized Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(parent, text="...", command=partial(ask_open_file, entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="SP model path").grid(row=1, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry_model)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output path").grid(row=2, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=2, column=2, padx=10, pady=5)


    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Tokenized Corpus path empty.")
            return

        sp_model = entry_model.get()
        if len(sp_model.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="SP model empty.")
            return

        tok_output = entry_output.get()
        if len(tok_output.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Output path empty.")
            return

        tok_output = os.path.join(tok_output, get_detok_file(corpus_file))

        print(corpus_file, sp_model, tok_output)

        sp = load_spm(sp_model)
        detokenize_file(sp, corpus_file, tok_output)

        tk.messagebox.showinfo(title="Info", message="Done")

    tk.Button(parent, text="DeTokenize with SP", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_noscores_corpus(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_input = tk.Entry(parent, width=50)
    entry_input.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_input)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_output)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_in = entry_input.get().strip()
        corpus_out = entry_output.get().strip()
        if len(corpus_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        if len(corpus_out) == 0:
            corpus_out = None

        strip_scores(corpus_in, corpus_out, logger=logger_opus)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Strip Scores from Scored TSV", command=go).grid(row=2, column=1, padx=10, pady=5)
