import click
import re
import requests
import time

from bs4 import BeautifulSoup as bs
# from config import BING_API_KEY
# from config import BING_SEARCH_ENDPOINT


BING_SEARCH_KEY = 'a461d635a4e0460b9a4aac7d5fbd3efa'
BING_API_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0'
BING_SEARCH_ENDPOINTS = {
    'suggestions': f'{BING_API_ENDPOINT}/suggestions',
    'entities': f'{BING_API_ENDPOINT}/entities',
    'images': f'{BING_API_ENDPOINT}/images',
    'visualsearch': f'{BING_API_ENDPOINT}/images/visualsearch',
    'news': f'{BING_API_ENDPOINT}/news',
    'spellcheck': f'{BING_API_ENDPOINT}/spellcheck',
    'videos': f'{BING_API_ENDPOINT}/videos',
    'search': f'{BING_API_ENDPOINT}/search'
}
BING_SEARCH_MARKET_CODE = {
    'Australia/English': 'en-AU',
    'Canada/English': 'en-CA',
    'Canada/French': 'fr-CA',
    'France/French': 'fr-FR',
    'Germany/German': 'de-DE',
    'India/English': 'en-IN',
    'Italy/Italian': 'it-IT',
    'Mexico/Spanish': 'es-MX',
    'United Kingdom/English': 'en-GB',
    'United States/English': 'en-US',
    'United States/Spanish': 'es-US',
    'Spain/Spanish': 'es-ES',
    'Brazil/Portuguese': 'pt-BR'
}


def search(endpoint: str='search', query: str=None,
           market: str='United States/English',
           search_extras: str= ' AND (intitle:about OR intitle:contact)',
           param_extras=None,
           verbose: bool=False):
    """Searches the BING API calling a specific endpoint

    Args:
        endpoint (str): endpoint to request from
            [suggestions, entities, images, visualsearch, news,
            spellcheck, videos, search] (Default search)
        query (str): search term
        market (str): market code to limit search to,
            for entities it is req (Default is US/English)

    Returns:
        json response (dict)

    """
    if endpoint not in BING_SEARCH_ENDPOINTS:
        print(
            "Endpoint is not valid." +
            f"Choose from [{'|'.join(BING_SEARCH_ENDPOINTS.keys())}]")
        return {}

    if not query:
        query = click.prompt("What do you want to search?")

    # Build Request
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_KEY}
    if endpoint == 'entities':
        params = {"q": query,
                  "mkt": BING_SEARCH_MARKET_CODE[market]}
    else:
        params = {"q": query + search_extras}

    if param_extras:
        for k, v in param_extras.items():
            params[k] = v

    if verbose:
        print('Bing Search...\n')
        print(f'Query: {query}')
        print(f'Params: {params}')

    # Request
    response = requests.get(
        BING_SEARCH_ENDPOINTS[endpoint], headers=headers, params=params)

    if verbose:
        print(f'Response code: {response}')
        print(f'{response.text}\n{response.json()}')

    return response.json()


def get_entities_from_search(query: str,
                             market: str='United States/English',
                             verbose: bool=False):
    """Return entities from search

    """
    res = search('entities', query=query, market=market, verbose=verbose)

    if verbose:
        print("\nSearching entities...\n")
        print(res)

    return res

    entities = {}
    try:
        for entity in res['entities']['value']:
            info = {}
            try:
                info['url'] = entity['url']
            except Exception:
                pass
            try:
                info['type'] = entity['entityPresentationInfo']['entityTypeHints']
            except Exception:
                pass
            try:
                info['description'] = entity['description']
            except Exception:
                pass
            entities[entity['name']] = info
    except BaseException:
        pass

    return entities


def get_urls(query: str, market: str='United States/English'):
    """Return search links from bing query

    Args:

    Returns:
        list of links
    """
    res = search('search', query, market)
    links = []
    try:
        for page in res['webPages']['value']:
            links.append(page['url'])
    except Exception:
        pass

    # res = search('search', query + " about", market)
    # try:
    #     for page in res['webPages']['value']:
    #         links.append(page['url'])
    # except Exception:
    #     pass

    # res = search('search', query + " contact", market)
    # try:
    #     for page in res['webPages']['value']:
    #         links.append(page['url'])
    # except Exception:
    #     pass

    if query.startswith('site:'):
        query = query[5:]
    time.sleep(.5)
    res = search('search', f'site:facebook.com {query}',
                 market,
                 search_extras='',
                 param_extras={'count': 1})
    try:
        for page in res['webPages']['value']:
            links.append(page['url'])
    except Exception:
        pass

    res = search('search', f'site:twitter.com {query}',
                 market,
                 search_extras='',
                 param_extras={'count': 1})
    try:
        for page in res['webPages']['value']:
            links.append(page['url'])
    except Exception:
        pass

    res = search('search', f'site:linkedin.com {query}',
                 market,
                 search_extras='',
                 param_extras={'count': 1})
    try:
        for page in res['webPages']['value']:
            links.append(page['url'])
    except Exception:
        pass

    return list(set(links))


def scrape_contact_from_url(site: str, market: str='United States/English',
                            get_entities: bool=False):
    links = get_urls(f'site:{site}', market=market)

    nums = []
    emails = []
    entities = []
    extras = []
    for link in links:
        phone, email, entity = scrape_url(link, get_entities=get_entities)
        if phone:
            for num in phone:
                if num not in nums:
                    nums.append(num)
        if email:
            for e in email:
                if e not in emails:
                    emails.append(e)
        if entity:
            for e in entity:
                if e not in entities:
                    entities.append(e)

    if get_entities:
        for entity in entities:
            extras.append(get_entities_from_search(entity, market=market))
    extras.append(get_entities_from_search(site.split('.')[0], market=market))
    return nums, emails, links, entities, extras


def scrape_url(url: str, get_entities: bool=False):
    """Scrapes a url for phone, email, and named entities

    """
    if get_entities:
        from srcs.ner import run_model
    try:
        html = requests.get(url, timeout=3, verify=False)
    except Exception as e:
        return [], [], []
    soup = bs(html.text, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()

    links = soup.find_all('a')
    phone = re.findall(
        r"((?:\d{3}|\(\d{3}\))?(?:\s|-|\.)?\d{3}(?:\s|-|\.)\d{4})", text)
    email_regex = re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}",
        re.IGNORECASE)
    emails = re.findall(email_regex, text)

    if get_entities:
        entities = [entity["text"]
                    for entity in run_model(text) if entity['text'] == 'PER']

    for link in links:
        try:
            ref = link.get('href')
            if ref.find('mailto:') > -1:
                email = re.match(email_regex, ref[7:])
                if email:
                    emails.append(email[0])
            elif ref.find('tel:') > -1:
                phone.append(ref[4:])
        except Exception:
            continue

    if get_entities:
        return set(phone), set(emails), set(entities)
    return set(phone), set(emails), []
