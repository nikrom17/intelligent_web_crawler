# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    linkedin_api.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/10 17:49:41 by nroman            #+#    #+#              #
#    Updated: 2018/04/11 13:54:11 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import colorama
import pandas as pd
import os
import requests
import json
import oauth2

from colorama import Fore, Back, Style
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

url_auth = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&state=wewillwinfirstpirze&scope=r_basicprofile"
url_search = "https://api.linkedin.com/v2/search?q=companiesV2&baseSearchParams.keywords="
search_terms = "automotive"
url_search = url_search + search_terms
url_token = "https://www.linkedin.com/oauth/v2/accessToken"

def process_search(results):
    link_list = [item["link"] for item in results["items"]]
    df = pd.DataFrame(link_list, columns=['link'])
    df["title"] = [item["title"] for item in results["items"]]
    df["snippet"] = [item["snippet"] for item in results["items"]]
    return df

try:
    CLIENT_ID = os.environ['CLIENT_ID_LI']
    print(CLIENT_ID)
    CLIENT_SECRET = os.environ['CLIENT_SEC_LI']
    print(CLIENT_SECRET)
except KeyError:
    raise SystemExit(Fore.RED + "Set your client ID and client secret as env variables")

class MyAuth(requests.auth.AuthBase):
    def __init__(self):
        client = BackendApplicationClient(response_type="code",
                                            client_id=CLIENT_ID,
                                            redirect_uri="https://www.linkedin.com/in/nikrom17/",
                                            state="wewillwinfirstplace")
        auth = OAuth2Session(client=client)
        self.token = auth.fetch_token(token_url=url_token , 
                                        code=client,
                                        client_id=CLIENT_ID,
                                        client_secret=CLIENT_SECRET)
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token['access_token']
        return r

response = requests.request("GET", url_search, auth=MyAuth())
print(response.keys())

"""
parameters =    {"q": search_terms,
                 "cx": cx,
                 "key": key,
                 "start": next_index
                }
"""

page = requests.request("GET", url_search)
results = json.loads(page.text)
#df = process_search(results)

print(results.keys())

print("status:")
print(results["status"])
print("message:")
print(results["message"])
print("serviceErrorCode:")
print(results["serviceErrorCode"])