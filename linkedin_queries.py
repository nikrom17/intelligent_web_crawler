from linkedin import linkedin

application = linkedin.LinkedInApplication(token='AQVrwHpVM74WSg6DHVRzb6TLyNCR9drlq0f-LoLnkkT2OUmXrtnkW3PKdbvYc46vFI-ecvDNDGyDdsGH5RvD8G4ex_A2QbjS3oYwV0J37icRTqdvLarKy7PuP6inQNCCHMd2EfYY8-ure7JtAS9u8gWnMqgSN-e7pVpKxT_LyTL2NSvPxD25pF_pDNQz8y8Bkijnsl6CBZWZ9ivDO3pLDgKsgoegaLpgrHz2EFa52yAYo5FtKicnGVAx82vnFByy5BNq6DXfR84oPwSobwFQzywYZsbWyKJRlo9Yc9Ty656-18dVNer0Oy3P7YVRXd-F5kM25OpmS2nPHw7BGFreQ-EWrzrGEg')


#Query fields: https://developer.linkedin.com/docs/fields/company-profile
companies = application.search_company(selectors=[{'companies': ['name', 'universal-name', 'website-url']}], params={'keywords': 'Innovation Network Platforms','facet':'location,us:84','facet':'industry,43'})

print(companies)