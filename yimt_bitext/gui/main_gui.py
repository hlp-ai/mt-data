from yimt_bitext.gui.frames import *


def on_menu(frame):
    for f in frames:
        if f == frame:
            f.pack()
        else:
            f.pack_forget()


if __name__ == "__main__":
    win_main = tk.Tk()
    win_main.title("平行语料处理软件")
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

    intersect_frame = tk.Frame(win_main)
    intersect_frame.pack()
    create_intersect_corpus(intersect_frame)
    frames.append(intersect_frame)

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

    han2Hans_frame = tk.Frame(win_main)
    han2Hans_frame.pack()
    create_han2hans_corpus(han2Hans_frame)
    frames.append(han2Hans_frame)

    no_scores_frame = tk.Frame(win_main)
    no_scores_frame.pack()
    create_noscores_corpus(no_scores_frame)
    frames.append(no_scores_frame)


    ####################################################################

    mainmenu = Menu(win_main)

    corpus_menu = Menu(mainmenu, tearoff=False)
    corpus_menu.add_command(label="解压", command=partial(on_menu, unzip_frame))
    corpus_menu.add_command(label="合并单语文件", command=partial(on_menu, merge_moses_frame))
    corpus_menu.add_command(label="合并平行语料", command=partial(on_menu, merge_frame))
    corpus_menu.add_command(label="规范化",command=partial(on_menu,normalize_frame))
    corpus_menu.add_command(label="去重", command=partial(on_menu, dedup_frame))
    corpus_menu.add_command(label="过滤",command=partial(on_menu,filter_frame))
    corpus_menu.add_command(label="分割语料文件", command=partial(on_menu, split_frame))
    corpus_menu.add_command(label="打分和过滤", command=partial(on_menu, score_filter_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="语料差异", command=partial(on_menu, diff_frame))
    corpus_menu.add_command(label="语料相交", command=partial(on_menu, intersect_frame))
    corpus_menu.add_command(label="取样", command=partial(on_menu, sample_frame))
    corpus_menu.add_command(label="划分语料", command=partial(on_menu, partition_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="退出", command=win_main.quit)

    mainmenu.add_cascade(label="处理管道", menu=corpus_menu)

    tsv_mono_menu = Menu(mainmenu, tearoff=False)
    tsv_mono_menu.add_command(label="平行到单语", command=partial(on_menu, tsv2mono_frame))
    tsv_mono_menu.add_command(label="单语到平行", command=partial(on_menu, mono2tsv_frame))

    mainmenu.add_cascade(label="单语-平行", menu=tsv_mono_menu)

    tokenize_menu = Menu(mainmenu, tearoff=False)
    tokenize_menu.add_command(label="训练SP模型", command=partial(on_menu, sp_train_frame))
    tokenize_menu.add_command(label="语料词条化", command=partial(on_menu, sp_tokenize_frame))
    tokenize_menu.add_command(label="语料去词条化", command=partial(on_menu, sp_detokenize_frame))
    tokenize_menu.add_separator()
    tokenize_menu.add_command(label="切分语料文件", command=partial(on_menu, tokenize_frame))
    tokenize_menu.add_command(label="中文语料去词条化", command=partial(on_menu, detokenize_frame))

    mainmenu.add_cascade(label="切分", menu=tokenize_menu)

    misc_menu = Menu(mainmenu, tearoff=False)
    misc_menu.add_command(label="语料统计", command=partial(on_menu, count_frame))
    misc_menu.add_command(label="繁体到简体", command=partial(on_menu, han2Hans_frame))
    misc_menu.add_command(label="剥离打分", command=partial(on_menu, no_scores_frame))

    mainmenu.add_cascade(label="杂项", menu=misc_menu)

    win_main.config(menu=mainmenu)

    ######################################################################

    for f in frames:
        f.pack_forget()

    win_main.mainloop()
