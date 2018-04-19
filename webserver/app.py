from flask import Flask,render_template, jsonify, request
from flask_cors import CORS
import re
from linkedin import linkedin
from linkedin_queries import linkedin_api
import clearbit
#from search_utils import scrape_url

clearbit.key = 'sk_8abade9a563c4a0f41ae1362f0dc1f12'

app = Flask(__name__,static_url_path='')
CORS(app)
#api = Api(app)

@app.route('/')
def showMachineList():
    return render_template('iws.html')

application = linkedin.LinkedInApplication(token='AQVrwHpVM74WSg6DHVRzb6TLyNCR9drlq0f-LoLnkkT2OUmXrtnkW3PKdbvYc46vFI-ecvDNDGyDdsGH5RvD8G4ex_A2QbjS3oYwV0J37icRTqdvLarKy7PuP6inQNCCHMd2EfYY8-ure7JtAS9u8gWnMqgSN-e7pVpKxT_LyTL2NSvPxD25pF_pDNQz8y8Bkijnsl6CBZWZ9ivDO3pLDgKsgoegaLpgrHz2EFa52yAYo5FtKicnGVAx82vnFByy5BNq6DXfR84oPwSobwFQzywYZsbWyKJRlo9Yc9Ty656-18dVNer0Oy3P7YVRXd-F5kM25OpmS2nPHw7BGFreQ-EWrzrGEg')


#Query fields: https://developer.linkedin.com/docs/fields/company-profile
def get_query(keywords):
	return application.search_company(selectors=[{'companies': ['name', 'universal-name', 'website-url', 'description', 'square-logo-url', 'specialties','locations']}], params={'keywords': keywords,'facet':'location,us:84'})
#query = application.get_companies(company_ids=[1035], selectors=['name'], params={'is-company-admin': 'true'})
# 1035 is Microsoft

#testq = application.get_companies(universal_names=['ideator-com'], selectors=['name'], params={'is-company-admin': 'true'})

query_data = []

@app.route('/iws/api/v1.0/companies', methods=['POST'])
def get_tasks():
	global query_data
	query_data = linkedin_api(request.get_json()["search"], request.get_json()["page"]*20, 20)
	#for q in query_data:
		#domain = re.split('^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)', q["websiteUrl"].lower())[1]
		#print(domain)
		# company = clearbit.Company.find(domain=domain, stream=True)
		# if company != None:
  #  			print (company["logo"])
	return jsonify(query_data)

@app.route('/companies/<string:name>', methods=['GET'])
def get_company(name):
	#print(query_data[0])
	comp = [query for query in query_data["data"] if query['universalName'] == name]
	comp[0]["websiteUrl"] = ("http://" +comp[0]["websiteUrl"], comp[0]["websiteUrl"])[comp[0]["websiteUrl"].startswith('http')]
	domain = re.split('^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)', comp[0]["websiteUrl"].lower())[1]
	newLInk ='http://'+ domain
	
	#print(newLInk)
	#phones,names, entities = scrape_url(newLInk)
	#print(phones)
	#print(names)
	#print("linkedin data:")
	#print(comp[0])
	#return render_template('detail.html', compData = comp[0], modelData = {'phones':phones,'names':names,'entities':entities})
	return render_template('detail.html', compData = comp[0])
	
if __name__ == "__main__":
    app.run()
