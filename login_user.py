import streamlit as st
from authenticator import login_authenticator

def start_login():
    name, authentication_status, username = login_authenticator.login(form_name='Login', location='main')
    if authentication_status:
        return authentication_status, login_authenticator, username
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Be sure you enter your username/password')

