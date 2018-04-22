import requests

from bs4 import BeautifulSoup as bs

def run():
    comp = 'Ideator, Inc.'
    html = requests.get(
        'http://www.buzzfile.com/Search/Company/Results?searchTerm=' +
        comp +
        '&type=1')
    soup = bs(html.text, "lxml")
    # print(soup)
    searchResult = (soup.select(
        '#companyList tr:nth-of-type(3) td:nth-of-type(2) a')[0]['href'])
    cpage = requests.get('http://www.buzzfile.com' + searchResult)
    soup = bs(cpage.text, "lxml")
    contactInfo = soup.select(
        '.company-info-box .company-info-box-title + .panel-collapse')[0]
    print(contactInfo.select('[itemprop="address"]')[0].text.strip())
    print(contactInfo.select('[itemprop="employee"]')[0].text.strip())
    print(contactInfo.select('[itemprop="contactType"]')[0].text.strip())
    print(contactInfo.select('[itemprop="telephone"]')[0].text.strip())

    bsInfo = soup.select(
        '.company-info-box .company-info-box-title + .panel-collapse')[2]
    print(bsInfo.select('[itemprop="description"]')[0].text.strip())

    foundedYear = soup.select(
        '.company-info-box-left .company-info-header span')
    print(foundedYear[0].text.strip())
    print(foundedYear[3].text.strip())
    print(foundedYear[5].text.strip())
    print(foundedYear[7].text.strip())

    bsinfo2 = soup.select('.company-info-box .my-table-td-header + td a')
    print(bsinfo2[0].text.strip())
    print(bsinfo2[1].text.strip())
    print(bsinfo2[2].text.strip())


if __name__ == "__main__":
    run()
