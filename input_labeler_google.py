# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    input_labeler_google.py                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/17 17:38:36 by nroman            #+#    #+#              #
#    Updated: 2018/04/17 22:20:37 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
import requests
import argparse
import webbrowser
import re
import os
from  googlesearch import search

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-query", help="Enter query")
    return (parser.parse_args())

def label_data(headers, full_header):
    labels = dict([("o", "\tB-ORG"), ("oo", "\tI-ORG"), ("p", "\tB-PER"), ("pp", "\tI-PER"), ("l", "\tB-LOC"), ("ll", "\tI-LOC"), ("m", "\tB-MISC"), ("mm", "\tI-MISC"), ("", "\t0")])
    l = len(headers)
    num = 1
    print(full_header[0])
    for i in range(l):
        if (headers[i] == '\n'):
            try:
                print(full_header[num])
            except:
                pass
            num += 1
            continue
        if not headers[i]:
            continue
        else:
            print(headers[i])
        while True:
            lbl_to_add = input("Enter label code[0]: ")
            print(lbl_to_add)
            if not lbl_to_add:
                headers[i] = headers[i].strip() + '\t' + labels["0"].strip()
            elif lbl_to_add in labels:
                headers[i] = headers[i].strip() + '\t' + labels[lbl_to_add].strip()
            else:
                print("invalid label: choose o, oo, p, pp, l, ll, m, mm, 0")
                continue
            break
    return (headers)

def linkedin_url_parser(results):
    urls = []
    for url in results:
        print(url)
        if 'www.linkedin.com/company' in url:
            temp = url.replace("-", " ")
            urls.append(temp[33:])
            urls.append('\n')
    urls = label_data(urls)
    write_to_file(urls)

def header_list_generator(results):
    headers = []
    for url in results:
        print(url)
        try:
            html = requests.request("GET", url, timeout=5)
            soup = bs(html.content, "lxml")
        except:
            continue
        for j in range(6):
            tag = 'h' + str(j)
            for listings in soup.find_all(tag, text=True):
                headers.append(listings.find_all(text=True)) 
    length = len(headers)
    new_headers = []
    for i in range(length):
        temp = [w for w in re.split('[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', headers[i][0])]
        temp_len = len(temp)
        for j in range(len(temp)):
            new_headers.append(temp[j])
        new_headers.append('\n')
    headers = label_data(new_headers, headers)
    write_to_file(new_headers)

def write_to_file(companies):
    input_file = open("list_of_headers1.txt", "a+")
    for x in companies:
        if (x  == '\n'): 
            input_file.write(str(x))
        elif (x):
            input_file.write(str(x) + '\n')
    input_file.close()

def write_to_file1(companies):
    with open("list_of_headers2.txt", "a+") as f:
        for header in companies:
            word, label = header.strip().split('\t')
            if word:
                    f.write(f'{word}\t{label}')

# format query in pandas format
def process_search(results):
    link_list = [item["link"] for item in results["items"]]
    df = pd.DataFrame(link_list, columns=['link'])
    df["title"] = [item["title"] for item in results["items"]]
    df["snippet"] = [item["snippet"] for item in results["items"]]
    return df

def google_custom_search_api(query):
    results = search(query, tld='com', lang='en', start=0, stop=1, pause=3.0)
    return results

def main():
    args = argument_parser()
    print(args.query)
    api_response = google_custom_search_api(args.query + "about us")
    header_list_generator(api_response)
    '''
    api_response = google_custom_search_api(args.query + "startup")
    header_list_generator(api_response)
    api_response = google_custom_search_api(args.query + "LinkedIn")
    linkedin_url_parser(api_response)
    '''

if __name__ == "__main__":
    main()
