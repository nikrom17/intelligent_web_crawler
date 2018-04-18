import glob
import os
import pandas as pd
import pickle
import string

from typing import Dict
from classifier import create_glove_vocab

DATA_DIR = os.path.abspath('./sentiment labelled sentences')
VOCAB_PATH = os.path.abspath('./models/glove_vocab.pickle')


def clean_sentence(sentence: str, vocab: Dict) -> str:
    tokens = sentence.split()
    table = str.maketrans('', '', string.punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [w for w in tokens if w in vocab]
    tokens = ' '.join(tokens)
    return tokens


def load_sentence_labelled():
    assert(os.path.exists(DATA_DIR))

    create_glove_vocab()
    with open(VOCAB_PATH, 'rb') as f:
        vocab = pickle.load(f)

    file_data = []
    for f in glob.glob(DATA_DIR + '/*_labelled.txt'):
        df = pd.read_csv(f, sep="\t", header=None, names=["sentence", "label"])
        df['sentence'] = df['sentence'].str.lower()
        df['sentence'] = df['sentence'].apply(
                lambda x: clean_sentence(x, vocab))
        file_data.append(df)
    data = pd.concat(file_data)

    print(f'\t{df[df["label"] == 1].size} positive labels')
    print(f'\t{df[df["label"] == 0].size} negative labels')
    return data
