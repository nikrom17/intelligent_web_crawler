from linkedin import linkedin

APPLICATON_KEY    = '86nf9ztg3050u4'
APPLICATON_SECRET = '11PtDgqF1GRkV7W5'

RETURN_URL = 'http://localhost:8000'

authentication = linkedin.LinkedInAuthentication(
                    APPLICATON_KEY,
                    APPLICATON_SECRET,
                    RETURN_URL,
                    linkedin.PERMISSIONS.enums.values()
                )

# Optionally one can send custom "state" value that will be returned from OAuth server
# It can be used to track your user state or something else (it's up to you)
# Be aware that this value is sent to OAuth server AS IS - make sure to encode or hash it
#authorization.state = 'your_encoded_message'

print (authentication.authorization_url)  # open this url on your browser
