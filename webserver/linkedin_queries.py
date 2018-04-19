from linkedin import linkedin
import re
from operator import itemgetter
import json

def flatten(seq,container=None):
    if container is None:
        container = []
    for s in seq:
        if hasattr(s,'__iter__'):
            flatten(s,container)
        else:
            container.append(s)
    return container

def linkedin_api(query, start, chunk):
    application = linkedin.LinkedInApplication(token='AQVrwHpVM74WSg6DHVRzb6TLyNCR9drlq0f-LoLnkkT2OUmXrtnkW3PKdbvYc46vFI-ecvDNDGyDdsGH5RvD8G4ex_A2QbjS3oYwV0J37icRTqdvLarKy7PuP6inQNCCHMd2EfYY8-ure7JtAS9u8gWnMqgSN-e7pVpKxT_LyTL2NSvPxD25pF_pDNQz8y8Bkijnsl6CBZWZ9ivDO3pLDgKsgoegaLpgrHz2EFa52yAYo5FtKicnGVAx82vnFByy5BNq6DXfR84oPwSobwFQzywYZsbWyKJRlo9Yc9Ty656-18dVNer0Oy3P7YVRXd-F5kM25OpmS2nPHw7BGFreQ-EWrzrGEg')

    #Query fields: https://developer.linkedin.com/docs/fields/company-profile
    companies = []
    tmp_query = application.search_company(selectors=[{'companies': ['name','website-url','industries', 'employee-count-range', 'specialties', 'locations', 'description','status']}], params={'keywords':query,'count':chunk, 'start':start})
    for company in tmp_query["companies"]["values"]:
        companies.append(dict(company))
    return sort_companies(companies, query)

def sort_companies(companies, query):
    company_size = {'B':10, 'C':10,'D':10, 'E':5, 'F':0, 'G':-10, 'H':-20, 'I':-20}
    ranked_list = []
    ordered_list = []
    print (query)
    parsed_query = re.split('[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', query)
    parsed_query = list(filter(None, parsed_query))
    print(companies[0])
    print(len(companies))
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

# def main():
#     query = input("query: ")
#     companies = linkedin_api(query)
#     ranked_list = sort_companies(companies, query)

    
if __name__ == "__main__":
    main()
