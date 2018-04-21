# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    buzzfile_scraper.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nroman <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2018/04/21 15:37:20 by nroman            #+#    #+#              #
#    Updated: 2018/04/21 16:15:15 by nroman           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from selenium import webdriver

browser = webdriver.Chrome(executable_path='./chromedriver')
browser.get('http://www.buzzfile.com/business/Tesla-650-681-5000')
browser.find_element_by_css_selector('#companyList tr:nth-child(2)').text
'Zilliant Incorporated\nHQ\n720 Brazos St\nAustin\nTX\n78701\n77\n30,122,331\nComputer Software Development'

>>> browser.find_element_by_css_selector('#companyList tr:nth-child(2) td:nth-child(2)').text
