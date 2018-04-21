# coding: utf-8

import click
import datetime
import numpy as np
import os
import pickle
import tensorflow as tf

from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.callbacks import TensorBoard
from keras.layers import Embedding
from keras.layers import Conv1D
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import GlobalMaxPooling1D
from keras.layers import Input
from keras.layers import Flatten
from keras.layers import LSTM
from keras.models import load_model
from keras.models import Model
from keras.layers import MaxPooling1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from typing import Tuple
from sys import exit

BASE_DIR = os.path.abspath('./')
BATCH_SIZE = 32
EMBEDDING_DIM = 200
EPOCHS = 100
LOG_DIR = os.path.join(BASE_DIR, 'logs')
MAX_SEQ_LENGTH = 100
MAX_NUM_WORDS = 10000
PATIENCE = 5
SAVE_DIR = os.path.join(BASE_DIR, 'models')
CHKPT_DIR = os.path.join(SAVE_DIR, 'checkpoints')
TOKENIZER_PATH = os.path.join(
    SAVE_DIR, f'tokenizer_{MAX_NUM_WORDS}.pickle')
PREPROCESSED_DATA_PATH = os.path.join(
    SAVE_DIR, f'preprocessed_data_{MAX_NUM_WORDS}_{MAX_SEQ_LENGTH}.pickle')
VALIDATION_SPLIT = .2
VOCAB_DIR = os.path.join(SAVE_DIR, 'glove_vocab.pickle')


class TrainValTensorBoard(TensorBoard):
    def __init__(self, log_dir='./logs', **kwargs):
        # Make the original `TensorBoard` log to a subdirectory 'training'
        training_log_dir = os.path.join(log_dir, 'training')
        super(TrainValTensorBoard, self).__init__(training_log_dir, **kwargs)

        # Log the validation metrics to a separate subdirectory
        self.val_log_dir = os.path.join(log_dir, 'validation')

    def set_model(self, model):
        # Setup writer for validation metrics
        self.val_writer = tf.summary.FileWriter(self.val_log_dir)
        super(TrainValTensorBoard, self).set_model(model)

    def on_epoch_end(self, epoch, logs=None):
        # Pop the validation logs and handle them separately with
        # `self.val_writer`. Also rename the keys so that they can
        # be plotted on the same figure with the training metrics
        logs = logs or {}
        val_logs = {k.replace('val_', ''): v for k,
                    v in logs.items() if k.startswith('val_')}
        for name, value in val_logs.items():
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.simple_value = value.item()
            summary_value.tag = name
            self.val_writer.add_summary(summary, epoch)
        self.val_writer.flush()

        # Pass the remaining logs to `TensorBoard.on_epoch_end`
        logs = {k: v for k, v in logs.items() if not k.startswith('val_')}
        super(TrainValTensorBoard, self).on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None):
        super(TrainValTensorBoard, self).on_train_end(logs)
        self.val_writer.close()


def create_glove_vocab() -> None:
    if os.path.exists(VOCAB_DIR):
        return

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

    with open(VOCAB_DIR, 'wb') as f:
        pickle.dump(dict(embeddings_index.keys()), f)


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
@click.option('--name', '-n', type=str, help="Model name",
              default=datetime.datetime.now().strftime("%Y_%d_%m_%I_%M"))
@click.option('--summary', '-s', is_flag=True)
def train(arch: str, log: bool, name: str, summary: bool):
    x_train, y_train, x_val, y_val = load_preprocess_data(
        PREPROCESSED_DATA_PATH)
    tokenizer = load_tokenizer(TOKENIZER_PATH)

    # Input Layers
    seq_input = Input(shape=(MAX_SEQ_LENGTH,), dtype='int32')
    embedding = load_glove_embeddings(tokenizer.word_index)(seq_input)

    print("Building model...")
    # Hidden Layers
    if arch == 'RNN':
        x = LSTM(100, dropout=0.2, return_sequences=True)(embedding)
        x = LSTM(50, dropout=0.2)(x)
        out = Dense(1, activation='sigmoid')(x)
    elif arch == 'CNN':
        x = Conv1D(64, 5, activation='relu')(embedding)
        x = Dropout(.2)(x)
        x = MaxPooling1D(4)(x)
        x = LSTM(50, dropout=0.2)(x)
        out = Dense(1, activation='sigmoid')(x)

    model = Model(seq_input, out)
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])

    if not os.path.exists(CHKPT_DIR):
        os.mkdir(CHKPT_DIR)
    model_checkpoint_path = os.path.join(CHKPT_DIR, name)
    callback_list = [
        EarlyStopping(monitor='val_loss', patience=PATIENCE, verbose=1),
        ModelCheckpoint(model_checkpoint_path, monitor='val_loss',
                        save_best_only=True)
    ]
    if log:
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        model_log_path = os.path.join(LOG_DIR, name)
        print(
            f'\tTraining is being logged. Run tensorboard --logdir={LOG_DIR}')
        print(f'\t\tModel Name: {name}')
        callback_list.append(TrainValTensorBoard(model_log_path,
                                                 histogram_freq=EPOCHS // 5,
                                                 write_grads=True,
                                                 write_graph=False,
                                                 batch_size=BATCH_SIZE))
    if summary:
        model.summary()
    print("Training Model...")
    model.fit(x_train, y_train,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              callbacks=callback_list,
              validation_data=(x_val, y_val),
              verbose=1)


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
