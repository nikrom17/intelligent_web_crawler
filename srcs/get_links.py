import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://google.com"


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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    chrome_driver_path = os.path.abspath("./chromedriver")
    if not os.path.exists(chrome_driver_path):
        raise IOError(
            f"Can't find web driver at {chrome_driver_path}." +
            "Did you download it?")
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              executable_path=chrome_driver_path)
    return driver


def get_links_from_search(query: str, num: int=None, start: int=0,
                          lang: str='en', wait_time: int=10):
    """Get links from Google Search

    Args:
        query (str): query to be used
        num (int):
        start (int):
        lang (str):
        wait_time (int):

    Returns:
        links (list): list of urls
    """

    driver = create_chrome_webdriver()
    search_url = f'{BASE_URL}/search?q={query}'

    if num:
        search_url += f'&num={num}'
    if start:
        search_url += f'&start={start}'
    search_url += f'&lang={lang}'

    driver.get(search_url)

    # Get Links
    links = []
    for ele in driver.find_elements_by_class_name("rc"):
        links.append(ele.find_element_by_xpath(".//a").get_attribute("href"))

    return links
