import clearbit
import re
import requests

from flask_cors import CORS
from flask import Flask, render_template, jsonify, request
from srcs.search_utils import scrape_url
from linkedin import linkedin
from linkedin_queries import linkedin_api
from srcs.bing_search_api import search as bing_search
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
application = linkedin.LinkedInApplication(
    token='AQWza0c5LYCMiNBq61PIbXR0-hbxmy3wS2LimHAB6J6adocMKAen6hUHzS31Lh9eMkscP5Nb35Fp2y-3Wfy1fSTFZRschEWmvG5CPE9-zJYy-o97kblbkoFxuzHTr1quMuJp8VbYI02mM3pPCzSYhOmOZAqATF77all48LZ1-s2YtKi503mI5Wkn2lTovIeHpJr7ZodSpg625cB8CpySixjWrB5czaKqezVEPemJVSwsRXzVizX5FbKjWBzHRAhIXqRNIstlU1gDPkZCIE-vymoplW97CZxVjky4MRePE2bgg23x7_8Up2kqzCEuuamH-l-KWaxvkvR_6JR2WNa4ubzMwvQ7CQ')


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
    bzData = getBuzzInfo(comp[0]["name"])
    yourf= (bzData.contactPerson)
    print(bzData)
    comp[0]["websiteUrl"] = (
        "http://" + comp[0]["websiteUrl"],
        comp[0]["websiteUrl"])[
        comp[0]["websiteUrl"].startswith('http')]
    domain = re.split(
        '^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)',
        comp[0]["websiteUrl"].lower())[1]
    newLInk = 'http://' + domain
    bingData = bing_search('entities', domain)
    
    #browser = webdriver.Chrome(executable_path='./chromedriver')
    #print(browser.get('http://www.buzzfile.com/Search/Company/Results?searchTerm='+ comp[0]["name"] +'&type=1'))
    #browser.get('http://www.buzzfile.com/Search/Company/Results?searchTerm='+ comp[0]["name"] +'&type=1')
    #browser.find_element_by_css_selector('#companyList tr:nth-child(2) td:nth-child(2) a').click()
    # if 'entities' in bingData:
    #     print(bingData)
    # else:
    #     bingData = bing_search('search', domain)
    #     print("search")
    #     print(bingData)
    return render_template('detail.html', compData=comp[0], buzzData=bzData, yourtData= )

def getBuzzInfo(name):

    data = {}
    html = requests.get('http://www.buzzfile.com/Search/Company/Results?searchTerm='+ name +'&type=1')
    soup = bs(html.text, "lxml")

    searchResult = (soup.select('#companyList tr:nth-of-type(3) td:nth-of-type(2) a')[0]['href'])
    data['src'] = 'http://www.buzzfile.com' + searchResult
    cpage = requests.get(data['src'])
    soup = bs(cpage.text, "lxml")
    contactInfo = soup.select('.company-info-box .company-info-box-title + .panel-collapse')[0]
    data['address'] = contactInfo.select('[itemprop="address"]')[0].text.strip()
    data['contactPerson'] = contactInfo.select('[itemprop="employee"]')[0].text.strip()
    data['contactTitle'] = contactInfo.select('[itemprop="contactType"]')[0].text.strip()
    data['contactPhone'] = contactInfo.select('[itemprop="telephone"]')[0].text.strip()

    bsInfo = soup.select('.company-info-box .company-info-box-title + .panel-collapse')[2]
    data['bsDesc'] = bsInfo.select('[itemprop="description"]')[0].text.strip()

    foundedYear = soup.select('.company-info-box-left .company-info-header span')
    data['fYear'] = foundedYear[0].text.strip()

    bsinfo2 = soup.select('.company-info-box .my-table-td-header + td a')
    data['sector'] = bsinfo2[0].text.strip()
    data['category'] = bsinfo2[1].text.strip()
    data['industry'] = bsinfo2[2].text.strip()

    return data 

if __name__ == "__main__":
    app.run()
