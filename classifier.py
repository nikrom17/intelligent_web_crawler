# coding: utf-8

import click
import numpy as np
import os
import pickle

from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.callbacks import TensorBoard
from keras.layers import Embedding
from keras.layers import Conv1D
from keras.layers import Dense
from keras.layers import GlobalMaxPooling1D
from keras.layers import Input
from keras.layers import LSTM
from keras.models import load_model
from keras.models import Model
from keras.layers import MaxPooling1D
from keras.layers import TimeDistributed
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from typing import Tuple
from sys import exit

BASE_DIR = os.path.abspath('./')
BATCH_SIZE = 128
EMBEDDING_DIM = 100
EPOCHS = 20
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MAX_SEQ_LENGTH = 1000
MAX_NUM_WORDS = 20000
PATIENCE = 5
SAVE_DIR = os.path.join(BASE_DIR, 'models')
TOKENIZER_PATH = os.path.join(SAVE_DIR, 'tokenizer.pickle')
PREPROCESSED_DATA_PATH = os.path.join(SAVE_DIR, 'preprocessed_data.pickle')
VALIDATION_SPLIT = .2


def load_glove_embeddings(word_index) -> np.ndarray:
    """Load Pre-trained GloVe Embeddings

    Args:
        word_index : Keras Tokenizer

    Return:
        embedding_matrix: Keras embedding layer
    """
    print("Loading pretrained GloVe Embeddings...")
    embeddings_index = {}
    embedding_path = os.path.join(BASE_DIR, f'glove.6B.{EMBEDDING_DIM}d.txt')

    if not os.path.exists(embedding_path):
        raise IOError(
            f"{embedding_path} not found. Download embeddings and unzip.")

    with open(embedding_path, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs

    num_words = min(MAX_NUM_WORDS, len(word_index) + 1)
    embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))
    for word, i in word_index.items():
        if i >= MAX_NUM_WORDS:
            continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

    embedding_layer = Embedding(num_words,
                                EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=MAX_SEQ_LENGTH,
                                trainable=False)

    return embedding_layer


def load_data() -> Tuple[np.ndarray, np.ndarray]:
    from tests.utils import load_sentence_labelled

    data = load_sentence_labelled()
    return data['sentence'].as_matrix(), data['label'].as_matrix()


@click.group()
def cli():
    pass


def preprocess_input_and_save() -> None:
    text, labels = load_data()

    print(f'\t{len(text)} training samples and {len(labels)} labels')
    tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
    tokenizer.fit_on_texts(text)

    print(f'\t{len(tokenizer.word_index)} unique words found.')
    sequences = tokenizer.texts_to_sequences(text)

    padded_sequences = pad_sequences(sequences, maxlen=MAX_SEQ_LENGTH)

    indices = np.arange(padded_sequences.shape[0])
    np.random.shuffle(indices)
    data = padded_sequences[indices]
    labels = labels[indices]
    num_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

    x_train = data[:-num_validation_samples]
    y_train = labels[:-num_validation_samples]
    x_val = data[-num_validation_samples:]
    y_val = labels[-num_validation_samples:]

    with open(TOKENIZER_PATH, 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(PREPROCESSED_DATA_PATH, 'wb') as f:
        pickle.dump((x_train, y_train, x_val, y_val), f)

    print('\tTraining data saved')


def load_preprocess_data(path: str) -> Tuple[np.ndarray,
                                             np.ndarray,
                                             np.ndarray,
                                             np.ndarray]:
    if not os.path.exists(path):
        print(f'Preprocessed data not found at {path}')
        if click.prompt(
                "Do you want to create Preprocessed data (may take awhile)?"):
            print("Create data...")
            if not os.path.exists(SAVE_DIR):
                os.mkdir(SAVE_DIR)
            if not os.path.exists(LOG_DIR):
                os.mkdir(LOG_DIR)
            preprocess_input_and_save()
        else:
            exit()

    print("Loading data...")
    with open(path, 'rb') as f:
        x_train, y_train, x_val, y_val = pickle.load(f)

    return x_train, y_train, x_val, y_val


def load_tokenizer(path: str) -> Tokenizer:
    if not os.path.exists(path):
        raise IOError(f'Tokenizer not found at {path}')

    with open(path, 'rb') as f:
        tokenizer = pickle.load(f)

    return tokenizer


@cli.command()
@click.option('--arch', '-a', type=click.Choice(['RNN', 'CNN']), default='RNN')
@click.option('--log', '-l', is_flag=True)
def train(arch: str, log: bool):
    x_train, y_train, x_val, y_val = load_preprocess_data(
        PREPROCESSED_DATA_PATH)
    tokenizer = load_tokenizer(TOKENIZER_PATH)

    # Input Layers
    seq_input = Input(shape=(MAX_SEQ_LENGTH,), dtype='int32')
    embedding = load_glove_embeddings(tokenizer.word_index)(seq_input)

    print("Building model...")
    # Hidden Layers
    if arch == 'RNN':
        x = LSTM(50, return_sequences=True)(embedding)
        out = TimeDistributed(Dense(1, activation='sigmoid'))(x)
    elif arch == 'CNN':
        x = Conv1D(128, 5, activation='relu')(embedding)
        x = MaxPooling1D(5)(x)
        x = Conv1D(128, 5, activation='relu')(x)
        x = MaxPooling1D(5)(x)
        x = Conv1D(128, 5, activation='relu')(x)
        x = GlobalMaxPooling1D()(x)
        x = Dense(128, activation='relu')(x)
        out = Dense(1, activation='sigmoid')(x)

    model = Model(seq_input, out)
    model.compile(loss='binary_crossentropy',
                  optimizer='adam')

    callback_list = [
        EarlyStopping(monitor='val_loss', patience=PATIENCE),
        ModelCheckpoint(SAVE_DIR, monitor='val_loss',
                        save_best_only=True)
    ]
    if log:
        callback_list.append(TensorBoard(LOG_DIR,
                                         histogram_freq=True,
                                         write_graph=True,
                                         batch_size=BATCH_SIZE))
    model.summary()

    model.fit(x_train, y_train,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              callbacks=callback_list,
              validation_data=(x_val, y_val))
    if log:
        print("Training was logged. Run tensorboard --logdir=<log_path>")


@cli.command()
@click.argument('model', type=click.Path(exists=True))
@click.argument('text_file', type=click.Path(exists=True))
def predict(path: str, text_file: str):
    model = load_model(path)
    tokenizer = load_tokenizer(TOKENIZER_PATH)

    with open(text_file, 'r') as f:
        text = f.read()

    if not text:
        raise IOError(f'No data in file ({text_file})')

    tokens = tokenizer.texts_to_sequences(text)
    data = pad_sequences(tokens, maxlen=MAX_SEQ_LENGTH)

    pred = model.predict(data)

    print(f'Predicted {pred}')


if __name__ == '__main__':
    cli()
