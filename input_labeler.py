# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    nn_input_creator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/14 19:42:05 by nroman            #+#    #+#              #
#    Updated: 2018/04/16 12:26:15 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.parse import quote_plus
import json
import requests
import argparse
import webbrowser
import re

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-query", help="Enter query")
    return (parser.parse_args())

def label_data(headers):
    labels = dict([("o", "\tB-ORG"), ("oo", "\tI-ORG"), ("p", "\tB-PER"), ("pp", "\tI-PER"), ("l", "\tB-LOC"), ("ll", "\tI-LOC"), ("m", "\tB-MISC"), ("mm", "\tI-MISC"), ("0", "\t0")])
    l = len(headers)
    for i in range(l):
        print(headers[i][0])
        while True:
            lbl_to_add = input("Enter lable code: ")
            print(lbl_to_add)
            try:
                headers[i][0] = headers[i][0] + labels[lbl_to_add]
            except:
                print("invalid label: choose o, oo, p, pp, l, ll, m, mm, 0")
                continue
            else:
                break
    return (headers)

def header_list_generator(results):
    length = len(results)
    headers = []
    print(length)
    for i in range(length):
        url = results["items"][i]["link"]
        print(url)
        html = requests.request("GET", url)
        soup = bs(html.content, "lxml")
        #headers.append(url)
        for j in range(6):
            tag = 'h' + str(j)
            for listings in soup.find_all(tag, text=True):
                headers.append(listings.find_all(text=True))
    print(len(headers))
    
    length = len(headers)
    new_headers = []
    for i in range(length):
        #print(headers[i][0])
        temp = [w for w in re.split('([^0-9A-Za-z])', headers[i][0]) if w]
       # print(temp)
        temp_len = len(temp)
        for j in range(len(temp)):
            if (temp[j].isalnum()):
        #        print(temp[j] + ":   " + str(temp[j].isalnum()))
                new_headers.append(temp[j])
        new_headers.append('\n')
    headers = label_data(headers)
    header_file = open("list_of_headers.txt", "a+")
    for i in range(len(new_headers)):
        if (new_headers[i] == '\n'): 
            header_file.write(str(new_headers[i]))
        else:
            header_file.write(str(new_headers[i]) + '\n')
    header_file.close()
    return(headers)

# format query in pandas format
def process_search(results):
    link_list = [item["link"] for item in results["items"]]
    df = pd.DataFrame(link_list, columns=['link'])
    df["title"] = [item["title"] for item in results["items"]]
    df["snippet"] = [item["snippet"] for item in results["items"]]
    return df

def google_custom_search_api(query):
    url = "https://www.googleapis.com/customsearch/v1"
    cx = "013712426752801183447:sbjpxtoakh4"
    key = "AIzaSyAH49BOT1KXhbmL8Lpf7OCD989JNyqXjzM"
    #next_index = 0
    parameters =    {"q": query,
                     "cx": cx,
                     "key": key
                    # "start": next_index
                    }
    page = requests.request("GET", url, params=parameters)
    results = json.loads(page.text)
    # I don't think we need to format the data in pandas just yet.
            # api_response = process_search(results)
    # Use if we want to check more than 10 results/query
             # next_index = results["queries"]["nextPage"][0]["startIndex"]
    return(results)

def main():
    args = argument_parser()
    #query = quote_plus(args.query)
    print(args.query)
    api_response = google_custom_search_api(args.query)
    print(api_response.keys())
    header_list_generator(api_response)
    return (api_response)

if __name__ == "__main__":
    main()
