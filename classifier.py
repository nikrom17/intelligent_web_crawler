# coding: utf-8

import numpy as np
import os

from keras.layers import Embedding
from keras.layers import Conv1D
from keras.layers import Dense
from keras.layers import GlobalMaxPooling1D
from keras.layers import Input
from keras.layers import LSTM
from keras.models import Model
from keras.layers import MaxPooling1D
from keras.layers import TimeDistributed
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from typing import Tuple
from typing import Dict

BASE_DIR = os.path.abspath('./')
BATCH_SIZE = 128
EMBEDDING_DIM = 100
EPOCHS = 20
NUM_LABELS = 1
MAX_SEQ_LENGTH = 1000
MAX_NUM_WORDS = 20000
VALIDATION_SPLIT = .2


def load_glove_embeddings(word_index) -> np.ndarray:
    """Load Pre-trained GloVe Embeddings

    Args:
        word_index : Keras Tokenizer

    Return:
        embedding_matrix: Keras embedding layer
    """
    embeddings_index = {}
    embedding_path = os.path.join(BASE_DIR, f'glove.6B.{EMBEDDING_DIM}d.txt')

    if not os.exists(embedding_path):
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
    pass


def preprocess_input() -> Tuple[Dict,
                                np.ndarray,
                                np.ndarray,
                                np.ndarray,
                                np.ndarray]:
    text, labels = load_data()

    tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
    tokenizer.fit_on_texts(text)

    sequences = tokenizer.texts_to_sequences(text)
    word_index = tokenizer.word_index

    padded_sequences = pad_sequences(sequences, maxlen=MAX_SEQ_LENGTH)

    indices = np.arange(padded_sequences.shape[0])
    np.random.shuffle(indices)
    data = pad_sequences[indices]
    labels = labels[indices]
    num_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

    x_train = data[:-num_validation_samples]
    y_train = labels[:-num_validation_samples]
    x_val = data[-num_validation_samples:]
    y_val = labels[-num_validation_samples:]

    return word_index, x_train, y_train, x_val, y_val


def model_train(network_type: str='RNN'):
    word_index, x_train, y_train, x_val, y_val = preprocess_input()

    # Input Layers
    seq_input = Input(shape=(MAX_SEQ_LENGTH,), dtype='int32')
    embedding = load_glove_embeddings(word_index)(seq_input)

    # Hidden Layers
    if network_type == 'RNN':
        x = LSTM(50, return_sequences=True)(embedding)

        # Output Layers
        out = TimeDistributed(Dense(1, activation='sigmoid'))(x)

    elif network_type == 'CNN':
        x = Conv1D(128, 5, activation='relu')(embedding)
        x = MaxPooling1D(5)(x)
        x = Conv1D(128, 5, activation='relu')(x)
        x = MaxPooling1D(5)(x)
        x = Conv1D(128, 5, activation='relu')(x)
        x = GlobalMaxPooling1D()(x)
        x = Dense(128, activation='relu')(x)
        out = Dense(NUM_LABELS, activation='sigmoid')(x)

    model = Model(seq_input, out)
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])

    model.fit(x_train, y_train,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              validation_data=(x_val, y_val))
