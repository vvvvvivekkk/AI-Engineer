"""
tokenize_demo.py - see how real tokenizers cut the same sentence into tokens.

Run:  python tokenize_demo.py "Your own sentence here"
Needs: transformers, tiktoken  (first run downloads small tokenizer files from Hugging Face)
"""
import sys                                   # sys.argv lets us read a sentence typed after the script name
import tiktoken                              # OpenAI's tokenizer library
from transformers import AutoTokenizer       # Hugging Face: loads the tokenizer that matches a model

# Use the sentence from the command line, or a default one with tricky words
text = sys.argv[1] if len(sys.argv) > 1 else "Tokenization isn't magic: unbelievably, ChatGPT reads tokens!"
print("Sentence:", text, "\n")

# --- Hugging Face tokenizers -------------------------------------------------
for name in ["bert-base-uncased", "gpt2", "HuggingFaceTB/SmolLM2-135M-Instruct"]:
    tok = AutoTokenizer.from_pretrained(name)        # download (once) and load the tokenizer
    pieces = tok.tokenize(text)                      # the text pieces (tokens)
    ids = tok(text)["input_ids"]                     # the token IDs the model actually receives
    print(f"{name}  (vocab size {tok.vocab_size:,})")
    print("  tokens:", pieces)
    print("  ids   :", ids)
    print("  count :", len(pieces), "\n")

# --- tiktoken encodings (used by OpenAI models) -------------------------------
for enc_name in ["cl100k_base", "o200k_base"]:
    enc = tiktoken.get_encoding(enc_name)            # load one encoding (vocabulary + merge rules)
    ids = enc.encode(text)                           # text -> list of integer IDs
    pieces = [enc.decode([i]) for i in ids]          # decode each ID alone to see its text piece
    print(f"tiktoken {enc_name}  (vocab size {enc.n_vocab:,})")
    print("  tokens:", pieces)
    print("  count :", len(ids))
    print("  round trip OK:", enc.decode(ids) == text, "\n")   # decoding all IDs gives the original text back
