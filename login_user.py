import streamlit as st
from authenticator import login_authenticator

def start_login():
    st.session_state.auth_status = False
    name, auth_status, username = login_authenticator.login(form_name='Login')
    if auth_status:
        st.session_state.auth_status = True
        return auth_status, login_authenticator, username
    elif st.session_state["auth_status"] == False:
        st.error('Username/password is incorrect')
    elif st.session_state["auth_status"] == None:
        st.warning('Be sure you enter your username/password')
