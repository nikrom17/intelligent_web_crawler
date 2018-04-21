import clearbit
import re

from flask_cors import CORS
from flask import Flask, render_template, jsonify, request
from srcs.search_utils import scrape_url
from linkedin import linkedin
from linkedin_queries import linkedin_api

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

# Look for related data of the company fron the web using google


@app.route('/companies/<string:name>', methods=['GET'])
def get_company(name):
    comp = [query for query in query_data["data"]
            if query['universalName'] == name]
    comp[0]["websiteUrl"] = (
        "http://" + comp[0]["websiteUrl"],
        comp[0]["websiteUrl"])[
        comp[0]["websiteUrl"].startswith('http')]
    domain = re.split(
        '^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)',
        comp[0]["websiteUrl"].lower())[1]
    newLInk = 'http://' + domain
    return render_template('detail.html', compData=comp[0])


if __name__ == "__main__":
    app.run()
