import re
import requests

from config import LINKEDIN_TOKEN
from flask_cors import CORS
from flask import Flask, render_template, jsonify, request
from linkedin import linkedin
from linkedin_queries import linkedin_api
from srcs.bing_search_api import get_entities_from_search
from srcs.bing_search_api import scrape_contact_from_url
from bs4 import BeautifulSoup as bs

app = Flask(__name__, static_url_path='')
CORS(app)


@app.route('/')
def showMachineList():
    return render_template('iws.html')


# Linkedin access token
# You can use this token for testing purposes
# to get a new code, please refer to
# https://developer.linkedin.com/docs/v2/oauth2-client-credentials-flow
application = linkedin.LinkedInApplication(LINKEDIN_TOKEN)


# Query fields: https://developer.linkedin.com/docs/fields/company-profile
def get_query(keywords):
    return application.search_company(
        selectors=[
            {
                'companies': [
                    'name',
                    'universal-name',
                    'website-url',
                    'description',
                    'square-logo-url',
                    'specialties',
                    'locations']}],
        params={
            'keywords': keywords,
            'facet': 'location,us:84'})


query_data = []

# Api to get the main data from linkedin


@app.route('/iws/api/v1.0/companies', methods=['POST'])
def get_tasks():
    global query_data
    query_data = linkedin_api(
        request.get_json()["search"],
        request.get_json()["page"] * 20,
        20)
    return jsonify(query_data)

# Look for related data of the company from the web using google


@app.route('/companies/<string:name>', methods=['GET'])
def get_company(name):
    comp = [query for query in query_data["data"]
            if query['universalName'] == name]
    bzData = getBuzzInfo(
        comp[0]["name"],
        comp[0]["locations"]["values"][0]["address"]["postalCode"])
    comp[0]["websiteUrl"] = (
        "http://" + comp[0]["websiteUrl"],
        comp[0]["websiteUrl"])[
        comp[0]["websiteUrl"].startswith('http')]
    domain = re.split(
        '^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)',
        comp[0]["websiteUrl"].lower())[1]

    # If you'd like to use the Deep Learning NER model to attempt to
    # grab named entities then you can pass 'get_entities=True'
    # into scrape_contact_from_url. It'll load the model and tensorflow,
    # return num, emails, links, entities, extras
    # The model needs to be trained more and it runs slowly so it's off by
    # default
    num, emails, links, _, extras = scrape_contact_from_url(
        domain, get_entities=False)

    bingData = {}
    bingData['sources'] = []

    # get social media data and links from Bing
    for link in links:
        if 'facebook' in link:
            bingData['facebook'] = link
        elif 'twitter' in link:
            bingData['twitter'] = link
        elif 'linkedin' in link:
            bingData['linkedin'] = link
        else:
            bingData['sources'].append(link)

    if bzData.contactPerson:
        bingData['person'] = get_entities_from_search(bzData.contactPerson)

    return render_template(
        'detail.html',
        compData=comp[0],
        buzzData=bzData,
        bingData=bingData)

# look for data on buzzfile page http://www.buzzfile.com/


def getBuzzInfo(name, postalCode):

    data = {}
    link = 'http://www.buzzfile.com/Search/Company/Results?searchTerm=' + \
        name + '&parameter=zipcode--' + postalCode + '&type=1'
    html = requests.get(link)
    soup = bs(html.text, "lxml")

    if (len(soup.select(
            '#companyList tr:nth-of-type(3) td:nth-of-type(2) a')) == 0):
        return 0
    else:
        searchResult = (
            soup.select(
                '#companyList tr:nth-of-type(3) td:nth-of-type(2) a')[0]['href'])
    data['src'] = 'http://www.buzzfile.com' + searchResult
    cpage = requests.get(data['src'])
    soup = bs(cpage.text, "lxml")
    contactInfo = soup.select(
        '.company-info-box .company-info-box-title + .panel-collapse')[0]
    data['address'] = contactInfo.select(
        '[itemprop="address"]')[0].text.strip()
    data['contactPerson'] = contactInfo.select(
        '[itemprop="employee"]')[0].text.strip()
    data['contactTitle'] = contactInfo.select(
        '[itemprop="contactType"]')[0].text.strip()
    data['contactPhone'] = contactInfo.select(
        '[itemprop="telephone"]')[0].text.strip()

    bsInfo = soup.select(
        '.company-info-box .company-info-box-title + .panel-collapse')[2]
    data['bsDesc'] = bsInfo.select('[itemprop="description"]')[0].text.strip()

    foundedYear = soup.select(
        '.company-info-box-left .company-info-header span')
    data['fYear'] = foundedYear[0].text.strip()

    bsinfo2 = soup.select('.company-info-box .my-table-td-header + td a')
    data['sector'] = bsinfo2[0].text.strip()
    data['category'] = bsinfo2[1].text.strip()
    data['industry'] = bsinfo2[2].text.strip()

    return data


if __name__ == "__main__":
    app.run()
