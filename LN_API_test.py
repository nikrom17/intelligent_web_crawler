# Credentials you get from registering a new application
client_id = '86nf9ztg3050u4'
client_secret = '11PtDgqF1GRkV7W5'

# OAuth endpoints given in the LinkedIn API documentation
authorization_base_url = 'https://www.linkedin.com/uas/oauth2/authorization'
token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix

linkedin = OAuth2Session(client_id, redirect_uri='http://127.0.0.1')
linkedin = linkedin_compliance_fix(linkedin)

# Redirect user to LinkedIn for authorization
authorization_url, state = linkedin.authorization_url(authorization_base_url)
print('Please go here and authorize,', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('Paste the full redirect URL here:')

# Fetch the access token
linkedin.fetch_token(token_url, client_secret=client_secret,
                     authorization_response=redirect_response)

# Fetch a protected resource, i.e. user profile
r = linkedin.get('https://api.linkedin.com/v1/people/~')
print(r.content)
