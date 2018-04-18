# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    nn_input_creator.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/14 19:42:05 by nroman            #+#    #+#              #
#    Updated: 2018/04/17 15:51:36 by nroman           ###   ########.fr        #
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
    headers = []
    for url in results:
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
        print(headers[i][0])
        #temp = [w for w in re.split('[^0-9A-Za-z\.\-]', headers[i][0])]
        temp = [w for w in re.split('[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', headers[i][0])]
        print(temp)
       # print(temp)
        temp_len = len(temp)
        for j in range(len(temp)):
        #        print(temp[j] + ":   " + str(temp[j].isalnum()))
            new_headers.append(temp[j])
        new_headers.append('\n')
   # headers = label_data(headers)
    header_file = open("list_of_headers.txt", "a+")
    for i in range(len(new_headers)):
        if (new_headers[i] == '\n'): 
            header_file.write(str(new_headers[i]))
        elif (new_headers[i]):
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
    next_index = 1
    results= []
    for i in range(3):
        parameters =    {"q": query,
                         "cx": cx,
                         "key": key,
                        "start": next_index
                        }
        page = requests.request("GET", url, params=parameters)
        temp = json.loads(page.text)
        print(temp.keys())
        next_index = temp["queries"]["nextPage"][0]["startIndex"]
        print(next_index)
        results.append(temp["items"][i]["link"])
        print(results)
        return(results)

def main():
    args = argument_parser()
    #query = quote_plus(args.query)
    print(args.query)
    for i in range(3):
        api_response = google_custom_search_api(args.query)
        header_list_generator(api_response)
    return (api_response)

if __name__ == "__main__":
    main()
