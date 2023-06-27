import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


def count_messages(dataframe):
    empty_df = pd.DataFrame(columns=['PLM', '24hrs', '48hrs', 'Last 5 days', 'Last 7 days'])
    # dataframe['payloaddatetime'] = pd.fro
    st.write(dataframe)
    # for plm in dataframe['PLM'].unique():
    #     empty_df = empty_df.append({'PLM': plm, '24hrs':None, '48hrs': None, 'Last 5 days': None, 'Last 7 days':None}, ignore_index=True)
    # st.write(empty_df)
