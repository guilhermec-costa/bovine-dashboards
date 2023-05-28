import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('credentials.yaml', 'r') as credentials:
    config = yaml.load(credentials, Loader=SafeLoader)

login_authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


# hashed_passwords = stauth.Hasher(['teste']).generate()
# print(hashed_passwords)