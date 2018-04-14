# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/13 08:26:20 by nroman            #+#    #+#              #
#    Updated: 2018/04/13 11:10:46 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from linkedin_scraper import Person
from linkedin_scraper import Company
from selenium import webdriver

driver = webdriver.Chrome('/nfs/2018/n/nroman/Downloads/chromedriver')
person = Person("https://www.linkedin.com/in/nikrom17/", driver=driver, scrape=False)
 
company = Company('https://www.linkedin.com/company/bmw', driver=driver, scrape=False)
company.scrape(close_on_complete=True)
