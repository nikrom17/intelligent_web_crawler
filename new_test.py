from linkedin_scraper import Person
from linkedin_scraper import Company
from selenium import webdriver
import os

print(os.environ['CHROMEDRIVER'])
driver = webdriver.Chrome(os.environ['CHROMEDRIVER'])
person = Person("https://www.linkedin.com/in/nikrom17/", driver=driver, scrape=False)
input("Please enter y after you have loged in")
company = Company('https://www.linkedin.com/company/bmw/')
company.scrape()
