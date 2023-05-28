import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('config.yaml', 'r') as credentials:
    config = yaml.load(credentials, Loader=SafeLoader)

login_authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# with open('config.yaml', 'w') as credentials:  
#     yaml.dump(config, credentials, default_flow_style=False)

if __name__ == '__main__':
    hashed_passwords = stauth.Hasher(['user2023']).generate()
    print(hashed_passwords)