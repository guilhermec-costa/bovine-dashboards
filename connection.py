import psycopg2 as pgsql
import streamlit as st

# string de conexão com o banco
@st.cache_resource
def start_connection():
    return pgsql.connect(**st.secrets['postgres'])
