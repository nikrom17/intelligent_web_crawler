# Intelligent Web Crawler
*Deployment Guide*

### Description
This web scraping program uses a combination of LinkedIn, Google and Clearbit APIs to generate a list of companies related to specific interest tags. The results are displayed using a custom algorithm to put companies Open Ecosystem Network would likely target (startups that are rapidly growing) first. The program uses a simple web interface to search and navigate the responses.


## Installation Instructions
1. NEED TO DOWNLOAD AND UNZIP CHROMEDRIVER FOR YOUR PLATFORM:

    depending on your chrome version you may also need to download a
    different version of the chrome driver. See the notes.txt files
    to see which version of Chrome is supported

    Our code was tested on Mac OSX with Chrome v62.0.3202.94
    with the following chromedriver:
https://chromedriver.storage.googleapis.com/index.html?path=2.35/

1. Install Python 3.6.5: https://www.python.org/downloads/
1. Install Python Packages: `pip install -r requirements.txt`


## Local Deployment
1. To start the webserver, implement the following command:
  1. `python3 app.py`
1. In a web browser navigate to:
  1. https://localhost:5000
1. Enter Query in search bar


## APIs
####  LinkedIn 
GET: https://api.linkedin.com/v2/search?q=companiesV2

####  Clearbit
GET: https://logo.clearbit.com/:domain
GET: https://company.clearbit.com/v2/companies/find?domain=:domain

#### Google
This program doesn't use a Google api. Instead, it uses a python package called selenium to automatically navigate google chrome to perform the querries. Google does not offer an API that provides the same functionality as a standard google search.  


## Notes

#### Create LinkedIn Application Account: https://www.linkedin.com/developer/apps
An accout is need to use the LinkedIn API. The Client ID and Secret are needed to get OAuth2 authorization. It is also recomended to set up a paid account. LinkedIn trottles API queries and a paid account will remove a lot of the limitations.

#### get Oauth2 Token
1. Copy client id and secrete to get_linkedin_token.py
1. Run get_linkedin_token.py
1. navigate to a web browser: http://localhost:8000/code
1. Enter your LinkedIn login information
1. You will recieve a token. This will last for 60 days.
1. Copy and paste this token into ```linkedin_queries.py``` on line 18.

#### Create Clearbit account: https://clearbit.com
Clearbit has a family of APIs that can be used to get information about any company. They allow 50 free querries a month. Prices for a paid plan range from \$100/month (2,500 queries/month) to \$500/month (25,000 queries/month)

The also offer additional packages. One of their biggest advantages is their integration with SalesForce.

To use the API, copy your Clearbit key to the file `app_clearbit.py`
![alt text](https://bytebucket.org/nikrom17/intelligent-web-crawler/raw/64546c4acfc2d7207ebe922f6a434c8fb76be69b/pics/CB.png?token=3aa383f6eb698c4f5baf98e6ad221518845deea5)

