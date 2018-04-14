# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    google_api.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/10 13:12:41 by nroman            #+#    #+#              #
#    Updated: 2018/04/14 12:01:37 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import pandas as pd
import requests
import json

def process_search(results):
    link_list = [item["link"] for item in results["items"]]
    df = pd.DataFrame(link_list, columns=['link'])
    df["title"] = [item["title"] for item in results["items"]]
    df["snippet"] = [item["snippet"] for item in results["items"]]
    return df

url = "https://www.googleapis.com/customsearch/v1"
cx = "013712426752801183447:sbjpxtoakh4"
key = "AIzaSyAH49BOT1KXhbmL8Lpf7OCD989JNyqXjzM"
search_terms = "innovation network platforms"
next_index = 0

parameters =    {"q": search_terms,
                 "cx": cx,
                 "key": key,
                 "start": next_index
                }
page = requests.request("GET", url, params=parameters)
results = json.loads(page.text)
df = process_search(results)
next_index = results["queries"]["nextPage"][0]["startIndex"]
"""
print("kind:")
print(results["kind"])
print("url:")
print(results["url"])
print("queries:")
print(results["queries"])
print("searchInformation:")
print(results["searchInformation"])
print("Items:")
print(results["items"])
"""
