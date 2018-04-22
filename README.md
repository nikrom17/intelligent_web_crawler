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

#### Bing
GET: https://api.cognitive.microsoft.com/bing/v7.0/search[?q][&count][&offset][&mkt][&safesearch]

GET: https://api.cognitive.microsoft.com/bing/v7.0/entities/[?q][&mkt][&count][&offset][&safesearch]

## Aditional APIs
####  Clearbit
GET: https://logo.clearbit.com/:domain

GET: https://company.clearbit.com/v2/companies/find?domain=:domain

## Notes

#### Create LinkedIn Application Account
An accout is need to use the LinkedIn API. The Client ID and Secret are needed to get OAuth2 authorization. It is also recomended to set up a paid account. LinkedIn trottles API queries and a paid account will remove a lot of the limitations.

#### get Oauth2 Token
1. Create a develop account for Linkedin: https://www.linkedin.com/developer/apps
1. Enter your login information (username and password), client id and secrete in `config.py` on lines 17-20
1. Run: ` python3 get_linkedin_token.py`
1. Your token will be displated on stdout and will be valid for 60 days.
1. Copy and paste this token into `config.py` on line 20.

#### Create Microsoft Azure Account
Micosoft has a very long free trial period, but it is recommend to sign up for a paid account.

This program uses the bing entity search (https://azure.microsoft.com/en-us/services/cognitive-services/bing-entity-search-api/) and bing custom search (https://azure.microsoft.com/en-us/services/cognitive-services/bing-custom-search/)

The custom seach is used to use the search the entire internet for companies matching the interest tags. The entity search is used to retrive detailed information on the companies found using the custom search. 

This program uses Bing instead of Google because there is no google API equivalent to a standard google search.

After an account is created:
1. Enter the keys for the search API in `config.py` on lines 30-31
1. Enter the keys for the Entiry Seach API in `config.py` on lines 32-323


![alt text](https://bitbucket.org/nikrom17/intelligent-web-crawler/raw/master/pics/bing.png)


#### Clearbit API: https://clearbit.com
Clearbit has a family of APIs that can be used to get information about any company. They allow 50 free querries a month. Prices for a paid plan range from \$100/month (2,500 queries/month) to \$500/month (25,000 queries/month)

The also offer additional packages. One of their biggest advantages is their integration with SalesForce.

To use the API, copy your Clearbit key to the file `app_clearbit.py`
![alt text](https://bytebucket.org/nikrom17/intelligent-web-crawler/raw/64546c4acfc2d7207ebe922f6a434c8fb76be69b/pics/CB.png?token=3aa383f6eb698c4f5baf98e6ad221518845deea5)

