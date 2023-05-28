import streamlit as st
from authenticator import login_authenticator
import yaml
from yaml.loader import SafeLoader
from authenticator import config

def register_user():
    try:
        if login_authenticator.register_user('Register user', preauthorization=False):
            st.success('New user registred successfully!')
    except Exception as error:
        st.error(error)