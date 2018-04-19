import click
import os

from ner import run_model
from search_and_label import get_headers_from_search

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@click.command()
@click.option('--query', '-q', type=str, prompt="What do you want to search?")
@click.option('--write', '-w', is_flag=True)
@click.option('--output_dir', '-dir', type=click.Path(),
              default=BASE_DIR)
@click.option('--output_file', '-o', type=str)
@click.option('--num', '-n', type=int, default=10)
@click.option('--exact_match', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
@click.option('--last_updated', '-l', type=click.Choice(['a', 'y', 'm', 'w']),
              default='a')
def cli(query: str, output_file: str, num: int,
        write: bool, output_dir: str, exact_match: bool, verbose: bool,
        last_updated: str) -> None:
    headers = get_headers_from_search(query=query, num=num,
                                      last_updated=last_updated,
                                      verbose=verbose,
                                      exact_match=exact_match)

    data = ' '
    for header in headers:
        header = ' '.join(header)
        data += f' {header}'
    entities = set([entity["text"] for entity in run_model(text=data)])
    for entity in entities:
        if len(entity) > 1:
            print(entity)


if __name__ == "__main__":
    cli()
