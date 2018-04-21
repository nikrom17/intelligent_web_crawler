# test code to show how ypu can obtain clearbit data

import clearbit
from config import KEY_CLEARBIT

clearbit.key = 'sk_8abade9a563c4a0f41ae1362f0dc1f12'

company = clearbit.Company.find(domain='thecheeseschool.com', stream=True)
if company is not None:
    print(company)
