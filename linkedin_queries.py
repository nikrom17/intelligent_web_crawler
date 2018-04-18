from linkedin import linkedin

def linkedin_api(query):
    application = linkedin.LinkedInApplication(token='AQVrwHpVM74WSg6DHVRzb6TLyNCR9drlq0f-LoLnkkT2OUmXrtnkW3PKdbvYc46vFI-ecvDNDGyDdsGH5RvD8G4ex_A2QbjS3oYwV0J37icRTqdvLarKy7PuP6inQNCCHMd2EfYY8-ure7JtAS9u8gWnMqgSN-e7pVpKxT_LyTL2NSvPxD25pF_pDNQz8y8Bkijnsl6CBZWZ9ivDO3pLDgKsgoegaLpgrHz2EFa52yAYo5FtKicnGVAx82vnFByy5BNq6DXfR84oPwSobwFQzywYZsbWyKJRlo9Yc9Ty656-18dVNer0Oy3P7YVRXd-F5kM25OpmS2nPHw7BGFreQ-EWrzrGEg')

    #Query fields: https://developer.linkedin.com/docs/fields/company-profile
    companies = []
    chunk = 0;
    while(chunk <= 60 or chunk > query["companies"]['_total']):
        query = application.search_company(selectors=[{'companies': ['name','website-url','industries', 'employee-count-range', 'specialties', 'locations', 'description']}], params={'keywords':query,'count':20, 'start':chunk})
        print("count: " + str(query["companies"]['_count']))
        print("start: " + str(query["companies"]['_start']))
        print("total: " + str(query["companies"]['_total']))
        for i in query["companies"]["values"]:
            print(i["name"])
            try:
                print(i["specialties"])
            except:
                print("No specialties....LAME")
            print("-------------------------------------------------------------------")
        for company in query["companies"]["values"]:
            companies.append(company)
        chunk += 20 
    return companies

def main():
    query = input("query: ")
    companies = linkedin_api(query)
    
if __name__ == "__main__":
    main()
