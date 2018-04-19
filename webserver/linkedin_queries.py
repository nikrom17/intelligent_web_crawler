from linkedin import linkedin
import re
from operator import itemgetter
import json

def linkedin_api(query, start, chunk):
    """uses the LinkedIn API to seach for companies based on the keywords entered

    Args:
        query (str): query to be used
        start (int): specify the start index of the API results
        chunk (int): specifiy the number of companies to return

    Returns:
        ranked list of companies matching query
    """

    application = linkedin.LinkedInApplication(token='AQXds9U0PuMOTTrEIAn_UU0HGJ6Oy54zIRwqBD8l6zAEHRDGO7gBxzJy7dS7PioiNcP_OnfTgKhDaI6phEodupviTrSDW9zD06ZhtWmz4KnyVdg2qaaBZFShMyrltEK80gyOls1zYr7PuheqK6vjAu7SZ119cIAR4OI_MWAjWODObZ0hBtS8wEGc4oRogkyEmY2ufFncjos9O8_LYjcOSjSN_oAn8A4DzsUhi9ZApxGTPtmgDWXfIy3wQj40BOub4ecwnz45sUqvTR9Qlpq43jMNbgxapJ-ADnEH4uZlQLijBSorurwNBMapn6-2-jhRkR_K2dWPdIiPWg-hAQug9YlBjpUF9w') 
    companies = []
    tmp_query = application.search_company(selectors=[{'companies': ['name','website-url','industries', 'employee-count-range', 'universal-name', 'email-domains', 'specialties', 'locations', 'description','status']}], params={'keywords':query,'count':chunk, 'start':start})
    for company in tmp_query["companies"]["values"]:
        companies.append(dict(company))
    return {'data':sort_companies(companies, query), 'total':tmp_query["companies"]["_total"] }

def sort_companies(companies, query):
    """rank the companies returned from the LinkeIn API

    ranks companies based on size, keyword frequency and operating status

    Args:
        companies (API response)
        query (str): query that generated the API response
    Returns:
        ranked list of companies matching query
    """
    company_size = {'B':10, 'C':10,'D':10, 'E':5, 'F':0, 'G':-10, 'H':-20, 'I':-20}
    ranked_list = [], ordered_list = []
    parsed_query = re.split('[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', query)
    parsed_query = list(filter(None, parsed_query))
    length = len(parsed_query)
    for company in companies:
        val = 0
        for i in range(length):
            try:
                val += company['description'].lower().count(parsed_query[i].lower())
            except:
                pass
            try:
                val += company['specialties']['values'].lower().count(parsed_query[i].lower())
            except:
                pass
            try:
                val += company['industries']['values'].lower().count(parsed_query[i].lower())
            except:
                pass
            try:
                val += company['name'].lower().count(parsed_query[i].lower())
            except:
                pass
        try:
            val += company_size[company['employeeCountRange']['code']]
            if (company_size[company['status']['code']] == 'OOB'):
                val = -100
        except:
            pass
        company['ranking'] = val
    companies.sort(key=lambda x: int(x['ranking']), reverse=True)
    json.dumps(companies)
    return companies

'''
def main():
     query = input("query: ")
     companies = linkedin_api(query, 0, 20)
if __name__ == "__main__":
    main()
'''
