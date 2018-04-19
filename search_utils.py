import os
import random
import re
import requests

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from ner import run_model
from urllib.parse import unquote

BASE_URL = "https://www.google.com"


def create_chrome_webdriver():
    """Creates a web driver for chrome

    NEED TO DOWNLOAD AND UNZIP CHROMEDRIVER FOR YOUR PLATFORM:

    depending on your chrome version you may also need to download a
    different version of the chrome driver. See the notes.txt files
    to see which version of Chrome is supported

    Our code was tested on Mac OSX with Chrome v62.0.3202.94
    with the following chromedriver:
    https://chromedriver.storage.googleapis.com/index.html?path=2.35/
    """
    chrome_options = Options()
    # May need to comment out headless if you aren't seeing results
    # Need to fill in captcha
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    chrome_driver_path = os.path.abspath("./chromedriver")
    if not os.path.exists(chrome_driver_path):
        raise IOError(
            f"Can't find web driver at {chrome_driver_path}." +
            "Did you download it?")
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              executable_path=chrome_driver_path)
    # Uncomment if you need to use the web browser
    # for captcha
    # driver.implicitly_wait(25)
    return driver


def get_links_from_search(query: str, num: int=None,
                          lang: str='en',
                          country: str='countryUS',
                          last_updated: str='y',
                          exact_match: bool=False,
                          verbose: bool=False):
    """Get links from Google Search

    Args:
        query (str): query to be used
        num (int):
        start (int):
        lang (str):
        wait_time (int):
        country (str):
        last_updated (str):

    Returns:
        links (list): list of urls
    """
    try:
        driver = create_chrome_webdriver()
    except Exception:
        return []

    search_url = _get_search_url(query, num, lang, country,
                                 last_updated, exact_match, verbose)

    driver.get(search_url)

    # Get Links
    links = []
    for ele in driver.find_elements_by_class_name("rc"):
        links.append(ele.find_element_by_xpath(".//a").get_attribute("href"))

    links = []
    # Search About Pages
    driver.get(f"{search_url}+inurl:about+us")

    # Get Links
    for ele in driver.find_elements_by_class_name("rc"):
        link = ele.find_element_by_xpath(".//a").get_attribute("href")
        if link not in links:
            links.append(link)

    # Search Contact Pages
    driver.get(f"{search_url}+inurl:contact+us")

    # Get Links
    for ele in driver.find_elements_by_class_name("rc"):
        link = ele.find_element_by_xpath(".//a").get_attribute("href")
        if link not in links:
            links.append(link)

    # Search Team Pages
    driver.get(f'{search_url}+inurl:"team"')

    # Get Links
    for ele in driver.find_elements_by_class_name("rc"):
        link = ele.find_element_by_xpath(".//a").get_attribute("href")
        if link not in links:
            links.append(link)

    driver.quit()
    links = random.shuffle(links)
    return links


def get_contact_from_search(url: str, num: int=5, start: int=0,
                            lang: str='en', wait_time: int=10,
                            last_updated: str='y',
                            verbose: bool=False):
    """Uses a Google Search to find potential contact URLS then scrapes

    """

    try:
        driver = create_chrome_webdriver()
    except Exception:
        return []

    search_url = f'{BASE_URL}/search?'

    if num:
        search_url += f'num={num}'
    if start:
        search_url += f'&start={start}'
    search_url += f'&hl={lang}'
    search_url += f'&tbs=qdr:{last_updated}'
    search_url += f"&q=site:{url}+-filetype:pdf"

    if verbose:
        print(f"Base Search URL: {search_url}\n")

    links = []
    # Search About Pages

    try:
        driver.get(f"{search_url}+inurl:about+us")

        # Get Links
        for ele in driver.find_elements_by_class_name("rc"):
            link = ele.find_element_by_xpath(".//a").get_attribute("href")
            if link not in links:
                links.append(link)
    except Exception:
        pass

    # Search Contact Pages
    try:
        driver.get(f"{search_url}+inurl:contact+us")

        # Get Links
        for ele in driver.find_elements_by_class_name("rc"):
            link = ele.find_element_by_xpath(".//a").get_attribute("href")
            if link not in links:
                links.append(link)
    except Exception:
        pass

    # Search Team Pages
    try:
        driver.get(f'{search_url}+inurl:team')

        # Get Links
        for ele in driver.find_elements_by_class_name("rc"):
            link = ele.find_element_by_xpath(".//a").get_attribute("href")
            if link not in links:
                links.append(link)
    except Exception:
        pass

    nums = []
    emails = []
    entities = []
    for link in links:
        phone, email, entity = scrape_url(link)
        if len(phone):
            for num in phone:
                if num not in nums:
                    nums.append(num)
        if len(email):
            for e in email:
                if e not in emails:
                    emails.append(e)
        if len(entity):
            for e in entity:
                if e not in entities:
                    entities.append(e)

    return {"phone": nums, "emails": emails, "entities": entities}


def scrape_url(url: str):
    """Scrapes a url for phone, email, and named entities

    """
    html = requests.get(url, timeout=5)
    soup = bs(html.text, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()

    links = soup.find_all('a')
    phone = re.findall(
        r"((?:\d{3}|\(\d{3}\))?(?:\s|-|\.)?\d{3}(?:\s|-|\.)\d{4})", text)
    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}",
        text)

    entities = [entity["text"]
                for entity in run_model(text) if entity["type"] == 'PER']

    for link in links:
        ref = link.get('href')
        if ref.find('mailto:') > -1:
            emails.append(ref[7:])
        elif ref.find('tel:') > -1:
            phone.append(ref[4:])

    return set(phone), set(emails), set(entities)


def get_html(url):
    header = {
        "User-Agent":
        "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
    try:
        html = requests.get(url, header=header, timeout=5)
        return (html)
    except Exception as e:
        print("Error accessing:", url)
        print(e)
        return None


def _get_search_url(query: str, num: int=None,
                    lang: str='en',
                    country: str='countryUS',
                    last_updated: str='y',
                    exact_match: bool=False,
                    verbose: bool=False):

    search_url = f'{BASE_URL}/search?'
    # Exclude Filetypes

    if num:
        search_url += f'num={num}'
    search_url += f'&hl={lang}'
    search_url += f'&tbs=qdr:{last_updated}'

    query = '+'.join(query.split())
    if exact_match:
        search_url += f'"&q={query}"'
    else:
        search_url += f'&q={query}'
    search_url += "+-filetype:pdf"

    if verbose:
        print(f"Base Search URL: {search_url}\n")

    return search_url


def _get_link(li):
    """Return external link from a search.

    """
    try:
        a = li.find("a")
        link = a["href"]
    except Exception:
        return None

    if link.startswith("/url?"):
        m = re.match('/url\?(url|q)=(.+?)&', link)
        if m and len(m.groups()) == 2:
            return unquote(m.group(2))

    return None
