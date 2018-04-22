import re
import json

from linkedin import linkedin


def linkedin_api(query, start, chunk):
    """ LinkedIn API Token
    Paste LinkedIn API token here.
    to get new token, run the following script:
    """

    application = linkedin.LinkedInApplication(
        token='AQXds9U0PuMOTTrEIAn_UU0HGJ6Oy54zIRwqBD8l6zAEHRDGO7gBxzJy7dS7PioiNcP_OnfTgKhDaI6phEodupviTrSDW9zD06ZhtWmz4KnyVdg2qaaBZFShMyrltEK80gyOls1zYr7PuheqK6vjAu7SZ119cIAR4OI_MWAjWODObZ0hBtS8wEGc4oRogkyEmY2ufFncjos9O8_LYjcOSjSN_oAn8A4DzsUhi9ZApxGTPtmgDWXfIy3wQj40BOub4ecwnz45sUqvTR9Qlpq43jMNbgxapJ-ADnEH4uZlQLijBSorurwNBMapn6-2-jhRkR_K2dWPdIiPWg-hAQug9YlBjpUF9w')

    # Query fields: https://developer.linkedin.com/docs/fields/company-profile
    companies = []
    tmp_query = application.search_company(
        selectors=[
            {
                'companies': [
                    'name',
                    'website-url',
                    'industries',
                    'employee-count-range',
                    'universal-name',
                    'email-domains',
                    'specialties',
                    'locations',
                    'description',
                    'status']}],
        params={
            'keywords': query,
            'count': chunk,
            'start': start,
            'facet': 'location,us:84',
            'facet': 'location,us:0'})
    try:
        for company in tmp_query["companies"]["values"]:
            companies.append(dict(company))
    except Exception:
        pass
    return {
        'data': sort_companies(
            companies,
            query),
        'total': tmp_query["companies"]["_total"]}


def sort_companies(companies, query):
    company_size = {
        'B': 10,
        'C': 10,
        'D': 10,
        'E': 5,
        'F': 0,
        'G': -10,
        'H': -20,
        'I': -20}
    parsed_query = re.split('[^0-9A-Za-z\.\-]|(?<!\w)[.]|[.](?!\w)', query)
    parsed_query = list(filter(None, parsed_query))
    length = len(parsed_query)
    for company in companies:
        val = 0
        for i in range(length):
            try:
                val += company['description'].lower().count(
                        parsed_query[i].lower())
            except BaseException:
                pass
            try:
                val += company['specialties']['values'].lower().count(
                        parsed_query[i].lower())
            except BaseException:
                pass
            try:
                val += company['industries']['values'].lower().count(
                        parsed_query[i].lower())
            except BaseException:
                pass
            try:
                val += company['name'].lower().count(
                        parsed_query[i].lower())
            except BaseException:
                pass
        try:
            val += company_size[company['employeeCountRange']['code']]
            if (company_size[company['status']['code']] == 'OOB'):
                val = -100
        except BaseException:
            pass
        company['ranking'] = val
    companies.sort(key=lambda x: int(x['ranking']), reverse=True)
    json.dumps(companies)
    return companies


def main():
    query = input("query: ")
    companies = linkedin_api(query, 0, 20)
    print(companies)


if __name__ == "__main__":
    main()
