import glob
import os
import pandas as pd


DATA_DIR = os.path.abspath('./sentiment labelled sentences')


def load_sentence_labelled():
    assert(os.path.exists(DATA_DIR))

    file_data = []
    for f in glob.glob(DATA_DIR + '/*_labelled.txt'):
        df = pd.read_csv(f, sep="\t", header=None, names=["sentence", "label"])
        df['sentence'] = df['sentence'].str.lower()
        file_data.append(df)
    data = pd.concat(file_data)
    return data
