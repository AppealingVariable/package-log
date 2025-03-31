import keyring as kr
import getpass

def set_creds():
    kr.set_password('package_email', input('Enter Email: '), getpass.getpass(prompt='Password: '))

set_creds()
