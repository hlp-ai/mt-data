""""Frame UI for train menu"""
import os
import tkinter as tk
import tkinter.messagebox
from functools import partial

from yimt_bitext.gui.win_utils import ask_open_file, ask_dir
from yimt_bitext.utils.sp import train_spm, load_spm, tokenize_file, detokenize_file


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

    tk.Label(parent, text="Max num of sentences").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_max_sentences = tk.Entry(parent)
    entry_max_sentences.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entry_max_sentences.insert(0, "5000000")

    tk.Label(parent, text="Character coverage").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_coverage = tk.Entry(parent)
    entry_coverage.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entry_coverage.insert(0, "0.9999")

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

        train_spm(corpus_file, sp_model, vocab_size,
                  num_sentences=entry_max_sentences.get(),
                  coverage=entry_coverage.get())

        tk.messagebox.showinfo(title="Info", message="SentencePiece model created.")

    tk.Button(parent, text="Train SentencePiece Model", command=go).grid(row=5, column=1, padx=10, pady=5)


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
