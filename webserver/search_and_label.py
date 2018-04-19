import click
import os
import re
import requests
import string

from bs4 import BeautifulSoup as bs
from search_utils import get_links_from_search
from typing import List

LABELS = dict([("o", "B-ORG"), ("oo", "I-ORG"), ("p", "B-PER"),
               ("pp", "I-PER"), ("l", "B-LOC"), ("ll", "I-LOC"),
               ("m", "B-MISC"), ("mm", "I-MISC"), ("", "O")])

DATA_DIR = os.path.abspath("./data")


def label_data(cleaned_headers: List, original_headers: List) -> List:
    """Label Data With User Input

    Args:
        cleaned_headers (list):
        full_headers (list):

    Return:
        labeled_headers (list):
    """
    labeled_headers = []
    header_size = len(cleaned_headers)
    for i, (clean, orig) in enumerate(zip(cleaned_headers, original_headers)):
        print("DATA LABELING:\n--------------\n")
        print(f"\nValid Labels: {LABELS}\nEnter 'h' to display labels.\n")
        print("Enter 's' to save already labeled data\n")
        print(f"\n[{i}/{header_size}]  '{orig}'\n")
        header = []
        if not click.prompt(f"Entities?", type=bool, default=False):
            for word in clean:
                header.append(f"{word}\t{LABELS['']}")
        else:
            for word in clean:
                lbl_to_add = click.prompt(
                    f"Enter label code for '{word}' ",
                    type=click.Choice(
                        list(LABELS.keys()) +
                        ["help", "h", "s"]),
                    default='')
                if lbl_to_add is "help" or lbl_to_add is "h":
                    print(LABELS)
                    lbl_to_add = click.prompt(
                        f"Enter label code for '{word}' ",
                        type=click.Choice(
                            list(LABELS.keys()) + ["b"]),
                        default='')
                if lbl_to_add is "s":
                    if header:
                        labeled_headers.append(header)
                    return labeled_headers

                header.append(f"{word}\t{LABELS[lbl_to_add]}")
        click.clear()
        labeled_headers.append(header)

    return labeled_headers


def header_list_generator(results: List, label: bool=True,
                          verbose: bool=True) -> List:
    headers = []
    if verbose:
        print("Links found: ")
    for url in results:
        if verbose:
            print(f"\t{url}")
        try:
            html = requests.request('GET', url, timeout=5)
            soup = bs(html.content, "lxml")
        except Exception:
            continue
        if soup.title and soup.title.string:
            headers.append(soup.title.string.strip())
        for tag in range(1, 3):
            for listings in soup.find_all(f'h{tag}', text=True):
                header = listings.get_text().strip()
                if header:
                    headers.append(header)
        for listings in soup.find_all("p", text=True):
            paragraph = listings.get_text().strip()
            if paragraph:
                headers.append(paragraph)

    # Clean headers
    cleaned_headers = []
    for header in headers:
        cleaned_headers.append([w for w in re.split(
            r'[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', header) if w])

    if verbose:
        print(f"\nNumber of headers found: {len(cleaned_headers)}")

    if label:
        cleaned_headers = label_data(cleaned_headers, headers)
    return cleaned_headers


def write_to_file(headers: List, output_dir: str, file_name: str) -> None:
    assert(os.path.exists(output_dir))
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "a+") as f:
        for header in headers:
            for line in header:
                f.write(f'{line}\n')
            f.write("\n")


def get_headers_from_search(query: str, num: int, last_updated: str,
                            exact_match: bool, verbose: bool,
                            label: bool=False) -> List:
    api_response = get_links_from_search(query, num=num, verbose=verbose)
    headers = header_list_generator(api_response, label=label)

    return headers


@click.command()
@click.option('--query', '-q', type=str, prompt="What do you want to search?")
@click.option('--extra_keywords', '-e', type=str, multiple=True)
@click.option('--write', '-w', is_flag=True)
@click.option('--output_dir', '-dir', type=click.Path(),
              default=DATA_DIR)
@click.option('--output_file', '-o', type=str)
@click.option('--num', '-n', type=int, default=5)
@click.option('--exact_match', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
@click.option('--last_updated', '-l', type=click.Choice(['a', 'y', 'm', 'w']),
              default='a')
def cli(query: str, output_file: str, num: int, extra_keywords, write: bool,
        output_dir: str, exact_match: bool, verbose: bool,
        last_updated: str) -> None:
    """Scrape Google search links for headers to extract named entities

    Args:
        query (str):
        output_file (str):
        num (int):

    """
    for keyword in extra_keywords:
        query += f" {keyword}"

    headers = get_headers_from_search(query=query, num=num,
                                      last_updated=last_updated,
                                      verbose=verbose,
                                      exact_match=exact_match,
                                      label=True)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(output_dir, "queries")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if write or click.prompt("Write to file?", type=bool):
        output_file = '_'.join(
            [w for w in query.split() if w not in string.punctuation]) + ".txt"
        print(f"Writing to {output_dir}/{output_file}")
        write_to_file(headers, output_dir, output_file)
    else:
        for header in headers:
            print(header)


if __name__ == "__main__":
    cli()
