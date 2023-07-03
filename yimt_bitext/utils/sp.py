""""Training and loading of SentencePiece model. Tokenize and detokenize text with SentencePiece model"""
import io
import sentencepiece as spm


def train_spm(corpus_fn,
              model_prefix,
              vocab_size,
              model_type="bpe",
              coverage=0.99995,
              num_sentences=5000000,
              add_dummy_prefix=False):
    """Train a SentencePiece model"""
    spm.SentencePieceTrainer.train(input=corpus_fn,
                                   model_prefix=model_prefix,
                                   vocab_size=vocab_size,
                                   model_type=model_type,
                                   character_coverage=coverage,
                                   input_sentence_size=num_sentences,
                                   shuffle_input_sentence=True,
                                   add_dummy_prefix=add_dummy_prefix)


def load_spm(sp_model_path):
    """Load SentencePiece model from file"""
    return spm.SentencePieceProcessor(model_file=sp_model_path)


def tokenize(sp_model, txt):
    """Tokenize text with SentencePiece

    :param sp_model: SentencePiece model
    :param txt: text or list of text
    :return: list of tokens
    """
    if not isinstance(txt, (list, tuple)):
        txt = [txt]
    tokens = sp_model.encode(txt, out_type=str)
    return tokens


def tokenize_file(sp_model, in_fn, out_fn):
    """Tokenize file with SentencePiece model and output result into file"""
    if isinstance(sp_model, str):
        sp_model = load_spm(sp_model)
    in_f = io.open(in_fn, encoding="utf-8")
    out_f = io.open(out_fn, "w", encoding="utf-8")
    sentences = 0
    tokens = 0
    for s in in_f:
        tok_s = tokenize(sp_model, s)[0]
        sentences += 1
        tokens += len(tok_s)
        if len(tok_s) > 0:
            out_f.write(" ".join(tok_s) + "\n")
        else:
            out_f.write("\n")
        if sentences % 100000 == 0:
            print("Sentences:", sentences, "Tokens:", tokens)
    print("Sentences:", sentences, "Tokens:", tokens)
    out_f.close()


def detokenize(sp_model, tokens):
    """Detokenize tokens into text"""
    return sp_model.decode(tokens)


def detok(tokens):
    """Simple detokenization for SentencePiece"""
    return " ".join(tokens).replace(" ", "").replace("▁", " ").strip()


def detokenize_file(sp_model, in_fn, out_fn):
    if isinstance(sp_model, str):
        sp_model = load_spm(sp_model)
    # in_f = io.open(in_fn, encoding="utf-8")
    tok_lines = io.open(in_fn, encoding="utf-8").readlines()
    tok_lines = [line.strip() for line in tok_lines]
    out_f = io.open(out_fn, "w", encoding="utf-8")
    for tokens in tok_lines:
        detok_line = detokenize(sp_model, tokens.split())
        out_f.write(detok_line + "\n")

    out_f.close()
