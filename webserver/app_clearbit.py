import clearbit

clearbit.key = 'sk_8abade9a563c4a0f41ae1362f0dc1f12'

company = clearbit.Company.find(domain='ideator.com', stream=True)
if company != None:
  print (company)
