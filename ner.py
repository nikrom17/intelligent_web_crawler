import anago
import click
import glob
import numpy as np
import os

from anago.reader import load_data_and_labels
from anago.reader import load_glove
from anago.tagger import Tagger
from typing import Tuple
from typing import List

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SAVE_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')
QUERIES_DIR = os.path.join(DATA_DIR, 'queries')
DATA_TRAIN = os.path.join(DATA_DIR, 'conll2003/en/ner')
EMBEDDING_PATH = os.path.join(DATA_DIR, 'glove.6B/glove.6B.100d.txt')
BASE_MODEL_PATH = os.path.join(SAVE_DIR, 'base_model')
CUSTOM_MODEL_PATH = os.path.join(SAVE_DIR, 'custom_model')

# Hyperparameters
PATIENCE = 3
VALIDATION_SPLIT = .2
BATCH_SIZE = 128
EPOCHS = 20


@click.group()
def cli():
    """Named Entity Recognizer for Web Parsing

    """
    pass


@cli.command()
@click.option('--batch_size', '-b', type=int, default=BATCH_SIZE)
@click.option('--max_epoch', '-e', type=int, default=EPOCHS)
@click.option('--patience', '-p', type=int, default=PATIENCE)
@click.option('--log_dir', '-l', type=click.Path(), default=LOG_DIR)
def train_base_model(batch_size: int, max_epoch: int, log_dir: str,
                     patience: int, no_log: bool) -> None:
    """Train a base NER model

    (Note: Not optimized for web parsing)

    Args:
        batch_size (int): number of batches to train on
        max_epoch (int): number of epochs to train the data on, early stopping
            is on by default
        patience (int); number of epochs to wait before stopping early
        log_dir (str): path to save tensorboard log information
        no_log (bool): don't log training data

    """
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    if not os.path.exists(BASE_MODEL_PATH):
        os.mkdir(BASE_MODEL_PATH)

    train_path = os.path.join(DATA_TRAIN, 'train.txt')
    valid_path = os.path.join(DATA_TRAIN, 'valid.txt')

    print('Loading data...')
    x_train, y_train = load_data_and_labels(train_path)
    x_valid, y_valid = load_data_and_labels(valid_path)
    print(len(x_train), 'train sequences')
    print(len(x_valid), 'valid sequences')

    embeddings = load_glove(EMBEDDING_PATH)

    if no_log:
        log_dir = None

    model = anago.Sequence(batch_size=batch_size, max_epoch=max_epoch,
                           log_dir=log_dir, embeddings=embeddings,
                           patience=patience)
    model.train(x_train, y_train, x_valid, y_valid)
    model.save(BASE_MODEL_PATH)


@cli.command()
@click.option('--log_dir', '-l', type=click.Path(), default=LOG_DIR)
def train(log_dir: str) -> None:
    """Fine-tune base model

    Args:
        log_dir (str): pth to save tensorboard log information

    """
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    x_train, y_train, x_valid, y_valid = train_test_split_from_queries()
    print(len(x_train), 'train sequences')
    print(len(x_valid), 'valid sequences')

    embeddings = load_glove(EMBEDDING_PATH)

    model = anago.Sequence(log_dir=LOG_DIR, embeddings=embeddings)
    model.load(BASE_MODEL_PATH)
    model.train(x_train, y_train, x_valid, y_valid)
    model.save(CUSTOM_MODEL_PATH)


@cli.command()
@click.argument('text_file', type=click.Path(exists=True))
@click.option('--model_dir', '-m',
              type=click.Path(),
              default=BASE_MODEL_PATH)
def predict(text_file: str, model_dir: str) -> None:
    """Performs NER analysis on text file

    (defaults to using base model which can be trained with train_base_model())

    Args:
        text_file (str): text file to perform analysis on
        model_dir (str): path to model to use for analysis

    """
    model = anago.Sequence.load(model_dir)

    with open(text_file, 'r') as f:
        text = f.read()

    data = text.split()
    pred = model.analyze(data)

    for entity in pred['entities']:
        print(entity)


@cli.command()
@click.argument('sentence', type=str)
@click.option('--model_dir', '-m',
              type=click.Path(),
              default=BASE_MODEL_PATH)
def test_model(sentence: str, model_dir: str) -> None:
    """Performs NER analysis on sentence

    (defaults to using base model which can be trained with train_base_model())

    Args:
        sentence (str): text file to perform analysis on
        model_dir (str): path to model to use for analysis

    """
    model = anago.Sequence.load(model_dir)
    tagger = Tagger(model.model, preprocessor=model.p)

    data = sentence.strip().split()
    pred = tagger.predict(data)
    tags = tagger._get_tags(pred)
    probs = tagger._get_prob(pred)
    res = tagger._build_response(data, tags, probs)

    print()
    print(list(zip(data, tags, probs)))
    print()

    if not res['entities']:
        print("No entities found.")
    else:
        print("Entities Found: ")

    for entity in res['entities']:
        print(f"\t{entity['text']} = {entity['type']}")


@cli.command()
@click.argument('text_file', type=click.Path(exists=True))
@click.option('--model_dir', '-m',
              type=click.Path(),
              default=BASE_MODEL_PATH)
def evaluate(text_file: str, model_dir: str):
    """Evaluates a models performance on a TSV file with word/label pairs


    Args:
        text_file (str): TSV text file to evaluate
        model_dir (str): path to model to use for analysis

    """
    model = anago.Sequence.load(model_dir)

    print('Loading data...')
    x_test, y_test = load_data_and_labels(text_file)

    model.eval(x_test, y_test)


def train_test_split_from_queries(
        split: float=.9) -> Tuple[np.ndarray, np.ndarray]:
    assert(os.path.exists(DATA_DIR))
    assert(os.path.exists(QUERIES_DIR))

    X, Y = np.array([]), np.array([])

    for data_file in glob.glob(f'{QUERIES_DIR}/*.txt'):
        x, y = modified_load_data_and_labels(data_file)
        X = np.concatenate((X, x), axis=0)
        Y = np.concatenate((Y, y), axis=0)

    split_idx = int(X.shape[0] * split)
    return X[:split_idx], Y[:split_idx], X[split_idx:], Y[split_idx:]


def modified_load_data_and_labels(filename):
    """Loads data and label from a file.

    Args:
        filename (str): path to the file.

        The file format is tab-separated values.
        A blank line is required at the end of a sentence.

        For example:
        ```
        EU	B-ORG
        rejects	O
        German	B-MISC
        call	O
        to	O
        boycott	O
        British	B-MISC
        lamb	O
        .	O

        Peter	B-PER
        Blackburn	I-PER
        ...
        ```

    Returns:
        tuple(numpy array, numpy array): data and labels.

    Example:
        >>> filename = 'conll2003/en/ner/train.txt'
        >>> data, labels = load_data_and_labels(filename)
    """
    sents, labels = [], []
    with open(filename) as f:
        words, tags = [], []
        for line in f:
            line = line.rstrip()
            if len(line) == 0 or line.startswith('-DOCSTART-'):
                if len(words) != 0:
                    if len(words) == 1:
                        words.append(' ')
                        tags.append('O')
                    sents.append(words)
                    labels.append(tags)
                    words, tags = [], []
            else:
                word, tag = line.split('\t')
                words.append(word)
                tags.append(tag)
    return np.asarray(sents), np.asarray(labels)


def load_model(model_dir: str=BASE_MODEL_PATH):
    assert(os.path.exists(BASE_MODEL_PATH))

    model = anago.Sequence.load(model_dir)
    return model


def run_model(text: str, model_dir: str=BASE_MODEL_PATH) -> List:
    """Performs NER analysis on sentence

    (defaults to using base model which can be trained with train_base_model())

    Args:
        text (str): text to perform analysis on
        model (str): path to model to use for analysis

    """
    model = anago.Sequence.load(model_dir)
    tagger = Tagger(model.model, preprocessor=model.p)

    data = text.strip().split()
    pred = tagger.predict(data)
    tags = tagger._get_tags(pred)
    probs = tagger._get_prob(pred)
    res = tagger._build_response(data, tags, probs)

    return res['entities']


if __name__ == '__main__':
    cli()
