import click
import requests

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


def search(endpoint: str, query: str, market: str='United States/English'):
    """Searches on the BING API calling a specific endpoint

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
    params = {"q": query}
    if endpoint == 'entities':
        params['mkt'] = BING_SEARCH_MARKET_CODE[market]

    # Request
    response = requests.get(
        BING_SEARCH_ENDPOINTS[endpoint], headers=headers, params=params)

    response.raise_for_status()
    results = response.json()
    return results
