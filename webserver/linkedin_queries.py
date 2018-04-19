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
    application = linkedin.LinkedInApplication(token='AQVuNZs8EupnF2NOY1RfHCNTWw5bp2CaiKsnFs21jipwBcswYvqLdCLL3VdYN9szx6iP3rEFqGwjUb5GouvMzgyNFitdF1QtxwpSUOSmar9D6BTMhzrByBuMQR-Bt4TKqz4kfAHvMHaN3bRsMlCjyD0BhfYF9j5j0-p8kwDFfQc_tNAJlrbC-yUE1ihRkyE3Gj2I07lWudlccPG3ozci-LWBdousbxbh0i3lLcg31HG4a_mb-uvdvaM0ZtwLs0-a7Xke5ohQaUqwruvVBVCGhS-jZtafYIx5KYqrOxCMTCywulHpM8SLYo8sd-606daWQ4wfAicrkOUV9FwM9TVeZk5x-aqkBQ')

    #Query fields: https://developer.linkedin.com/docs/fields/company-profile
    companies = []
    val = 0
    total_chunk = chunk
    while (val < total_chunk):
        print(val)
        try:
            tmp_query = application.search_company(selectors=[{'companies': ['name','website-url','industries', 'employee-count-range', 'square-logo-url', 'universal-name', 'specialties', 'locations', 'description','status']}], params={'keywords':query,'count':chunk, 'start':start})
            print(tmp_query)
            val += chunk
            start += chunk
            for company in tmp_query["companies"]["values"]:
                companies.append(dict(company))
        except:
            chunk -= 5
            print(chunk)
            if (chunk < 1):
                chunk = 1

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

def main():
     query = input("query: ")
     companies = linkedin_api(query, 0, 20)


    
if __name__ == "__main__":
    main()
