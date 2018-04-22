import time

from config import CLIENT_ID_LI
from config import CLIENT_SEC_LI
from linkedin.linkedin import LinkedInAuthentication
from linkedin.linkedin import LinkedInApplication
from config import LINKEDIN_USER_NAME
from config import LINKEDIN_PSWRD
from selenium import webdriver


if __name__ == '__main__':

    CLIENT_ID = CLIENT_ID_LI
    CLIENT_SECRET = CLIENT_SEC_LI
    RETURN_URL = 'http://localhost:8000/code'

    authentication = LinkedInAuthentication(
        CLIENT_ID,
        CLIENT_SECRET,
        RETURN_URL,
        permissions=['r_basicprofile',
                     'r_emailaddress',
                     'rw_company_admin',
                     'w_share']
    )

    # Note: edit permissions according to what you defined in the linkedin
    # developer console.

    # Optionally one can send custom "state" value that will be returned from
    # OAuth server It can be used to track your user state or something else
    # (it's up to you) Be aware that this value is sent to OAuth server AS IS -
    # make sure to encode or hash it
    # authorization.state = 'your_encoded_message'

#    print(authentication.authorization_url)
    application = LinkedInApplication(authentication)
    browser = webdriver.Chrome(executable_path='./chromedriver')
    browser.get(authentication.authorization_url)
    time.sleep(10)
    username = browser.find_element_by_id("session_key-oauth2SAuthorizeForm")
    password = browser.find_element_by_id(
        "session_password-oauth2SAuthorizeForm")
    username.send_keys(LINKEDIN_USER_NAME)
    password.send_keys(LINKEDIN_PSWRD)
    login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
    login_attempt.submit()
    token_url = browser.current_url
    token = token_url.split('&')
    token = token[0][32:]
    print(token)
