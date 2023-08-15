import tkinter as tk
from functools import partial
from tkinter import *

from yimt_bitext.gui.corpus_frame import create_tsv2mono_corpus, create_mono2tsv_corpus, create_unzip_corpus, \
    create_merge_corpus, create_merge_moses_corpus, create_normalize_corpus, create_filter_corpus, \
    create_score_filter_corpus, create_dedup_corpus, create_han2hans_corpus, \
    create_sample_corpus, create_partition_corpus, create_split_corpus, create_tok_mono, create_detok_zh, \
    create_diff_corpus, create_count
from yimt_bitext.gui.train_frame import create_sp_train, create_sp_tokenize, create_sp_detokenize


def on_menu(frame):
    for f in frames:
        if f == frame:
            f.pack()
        else:
            f.pack_forget()


if __name__ == "__main__":
    win_main = tk.Tk()
    win_main.title("MT Pipeline")
    win_main.geometry("800x700")

    ##########################################################

    frames = []

    tsv2mono_frame=tk.Frame(win_main)
    tsv2mono_frame.pack()
    create_tsv2mono_corpus(tsv2mono_frame)
    frames.append(tsv2mono_frame)

    mono2tsv_frame = tk.Frame(win_main)
    mono2tsv_frame.pack()
    create_mono2tsv_corpus(mono2tsv_frame)
    frames.append(mono2tsv_frame)

    unzip_frame = tk.Frame(win_main)
    unzip_frame.pack()
    create_unzip_corpus(unzip_frame)
    frames.append(unzip_frame)

    merge_frame = tk.Frame(win_main)
    merge_frame.pack()
    create_merge_corpus(merge_frame)
    frames.append(merge_frame)

    merge_moses_frame = tk.Frame(win_main)
    merge_moses_frame.pack()
    create_merge_moses_corpus(merge_moses_frame)
    frames.append(merge_moses_frame)

    normalize_frame = tk.Frame(win_main)
    normalize_frame.pack()
    create_normalize_corpus(normalize_frame)
    frames.append(normalize_frame)

    filter_frame=tk.Frame(win_main)
    filter_frame.pack()
    create_filter_corpus(filter_frame)
    frames.append(filter_frame)

    score_filter_frame = tk.Frame(win_main)
    score_filter_frame.pack()
    create_score_filter_corpus(score_filter_frame)
    frames.append(score_filter_frame)

    dedup_frame = tk.Frame(win_main)
    dedup_frame.pack()
    create_dedup_corpus(dedup_frame)
    frames.append(dedup_frame)

    diff_frame = tk.Frame(win_main)
    diff_frame.pack()
    create_diff_corpus(diff_frame)
    frames.append(diff_frame)

    han2Hans_frame = tk.Frame(win_main)
    han2Hans_frame.pack()
    create_han2hans_corpus(han2Hans_frame)
    frames.append(han2Hans_frame)

    sample_frame = tk.Frame(win_main)
    sample_frame.pack()
    create_sample_corpus(sample_frame)
    frames.append(sample_frame)

    partition_frame = tk.Frame(win_main)
    partition_frame.pack()
    create_partition_corpus(partition_frame)
    frames.append(partition_frame)

    split_frame = tk.Frame(win_main)
    split_frame.pack()
    create_split_corpus(split_frame)
    frames.append(split_frame)

    tokenize_frame = tk.Frame(win_main)
    tokenize_frame.pack()
    create_tok_mono(tokenize_frame)
    frames.append(tokenize_frame)

    detokenize_frame = tk.Frame(win_main)
    detokenize_frame.pack()
    create_detok_zh(detokenize_frame)
    frames.append(detokenize_frame)

    sp_train_frame = tk.Frame(win_main)
    sp_train_frame.pack()
    create_sp_train(sp_train_frame)
    frames.append(sp_train_frame)

    sp_tokenize_frame = tk.Frame(win_main)
    sp_tokenize_frame.pack()
    create_sp_tokenize(sp_tokenize_frame)
    frames.append(sp_tokenize_frame)

    sp_detokenize_frame = tk.Frame(win_main)
    sp_detokenize_frame.pack()
    create_sp_detokenize(sp_detokenize_frame)
    frames.append(sp_detokenize_frame)

    count_frame = tk.Frame(win_main)
    count_frame.pack()
    create_count(count_frame)
    frames.append(count_frame)


    ####################################################################

    mainmenu = Menu(win_main)

    corpus_menu = Menu(mainmenu, tearoff=False)
    corpus_menu.add_command(label="Unzip Files", command=partial(on_menu, unzip_frame))
    corpus_menu.add_command(label="Merge Moses Files", command=partial(on_menu, merge_moses_frame))
    corpus_menu.add_command(label="Merge Files", command=partial(on_menu, merge_frame))
    corpus_menu.add_command(label="Normalize",command=partial(on_menu,normalize_frame))
    corpus_menu.add_command(label="Dedup", command=partial(on_menu, dedup_frame))
    corpus_menu.add_command(label="Filter",command=partial(on_menu,filter_frame))
    corpus_menu.add_command(label="Split", command=partial(on_menu, split_frame))
    corpus_menu.add_command(label="Score and Filter", command=partial(on_menu, score_filter_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Diff", command=partial(on_menu, diff_frame))
    corpus_menu.add_command(label="Sample", command=partial(on_menu, sample_frame))
    corpus_menu.add_command(label="Partition", command=partial(on_menu, partition_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Exit", command=win_main.quit)

    mainmenu.add_cascade(label="Opus", menu=corpus_menu)

    tsv_mono_menu = Menu(mainmenu, tearoff=False)
    tsv_mono_menu.add_command(label="TSV2Mono", command=partial(on_menu, tsv2mono_frame))
    tsv_mono_menu.add_command(label="Mono2TSV", command=partial(on_menu, mono2tsv_frame))

    mainmenu.add_cascade(label="TSV-Mono", menu=tsv_mono_menu)

    tokenize_menu = Menu(mainmenu, tearoff=False)
    tokenize_menu.add_command(label="Train SP", command=partial(on_menu, sp_train_frame))
    tokenize_menu.add_command(label="Tokenize with SP", command=partial(on_menu, sp_tokenize_frame))
    tokenize_menu.add_command(label="DeTokenize with SP", command=partial(on_menu, sp_detokenize_frame))
    tokenize_menu.add_separator()
    tokenize_menu.add_command(label="Tokenize File", command=partial(on_menu, tokenize_frame))
    tokenize_menu.add_command(label="DeTokenize Chinese Text", command=partial(on_menu, detokenize_frame))

    mainmenu.add_cascade(label="Tokenize", menu=tokenize_menu)

    misc_menu = Menu(mainmenu, tearoff=False)
    misc_menu.add_command(label="Count", command=partial(on_menu, count_frame))
    misc_menu.add_command(label="Hant2Hans", command=partial(on_menu, han2Hans_frame))

    mainmenu.add_cascade(label="Misc", menu=misc_menu)

    win_main.config(menu=mainmenu)

    ######################################################################

    for f in frames:
        f.pack_forget()

    win_main.mainloop()
