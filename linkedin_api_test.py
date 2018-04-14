# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    linkedin_api.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/10 17:49:41 by nroman            #+#    #+#              #
#    Updated: 2018/04/12 08:40:38 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import colorama
import pandas as pd
import os
import requests
import json
import oauth2
import company.py

from colorama import Fore, Back, Style
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

company = Company("https://www.linkedin.com/company/bmw")
