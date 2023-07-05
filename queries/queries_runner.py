import streamlit as st
import pandas as pd
import psycopg2 as pgsql
    
class Queries:
    def __init__(self):
        self.all_queries_commands = []
        self.all_queries_names = []
        self.results = {}
        self.connection = Connection.start_connection()

    @st.cache_resource
    def start_connection():
        try:
            return pgsql.connect(**st.secrets['postgres'])
        except Exception:
            st.error('Failed to connect to database.')
            return None

    def add_queries(self, const_list: list):
        for constant in const_list:
            self.all_queries_commands.append(constant[0])
            self.all_queries_names.append(constant[1])
    
    def get_query_result(self):
        return self.results

    def show_queries(self):
        st.write(self.all_queries_commands)

    @st.cache_data(ttl=600)
    def run_queries(_self):
        with _self.connection.cursor() as cursor:
            for query_name, query in enumerate(_self.all_queries_commands):
                cursor.execute(query)
                _self.results[_self.all_queries_names[query_name]] = cursor.fetchall()
        return _self.results

class Connection(Queries):
    def start_connection():
        try:
            return pgsql.connect(**st.secrets['postgres'])
        except Exception:
            st.error('Failed to connect to database.')
            return None
