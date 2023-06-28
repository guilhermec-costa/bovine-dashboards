import streamlit as st
import datetime
import pytz

style_markdown_warning = """
color: rgb(255, 255, 194);
background-color: rgba(255, 227, 18, 0.2);
border-radius: 5px;
height: 55px;
display: flex;
align-items: center;
vertical-align: middle;
padding-left: 14px;
margin: 4px;
"""
style_markdown_error = """
color: rgb(255, 222, 222);
background-color: rgba(255, 108, 108, 0.2);
border-radius: 5px;
height: 55px;
display: flex;
align-items: center;
vertical-align: middle;
padding-left: 14px;
margin: 4px;
"""
class Filters:
    def __init__(self, data_frame):
        self.df = data_frame
        self.c1_date, self.c2_date = st.columns(2)

    def apply_date_filter(self, start, end, refer_column:str, trigger_error=False):
        if start <= end:
            self.df = self.df[(self.df[refer_column] >= start) & (self.df[refer_column] <= end)]
            return
        
        default_start_date = datetime.datetime.now(tz=pytz.timezone('Brazil/East'))  - datetime.timedelta(days=1)
        default_end_date = datetime.datetime.now(tz=pytz.timezone('Brazil/East')) + datetime.timedelta(days=1)
        self.df = self.df[(self.df[refer_column] >= default_start_date) &
                            (self.df[refer_column] <= default_end_date)]
        if trigger_error:
            self.c1_date.write(f'<div style="{style_markdown_error}">There is no data. Start date set to {default_start_date.strftime("%Y-%m-%d %H:%M:%S")} and end date set to {default_end_date.strftime("%Y-%m-%d %H:%M:%S")}.</div>',
                               unsafe_allow_html=True)
            self.c2_date.write(f'<div style="{style_markdown_warning}">Verify if START DATE is greater than END DATE. </div>', unsafe_allow_html=True)

    def apply_time_filter(self, start_time, end_time, trigger_error=False):
        if start_time <= end_time:
            self.df = self.df[(self.df['Time'] >= start_time) & (self.df['Time'] <= end_time)]
            return
        default_start_time = datetime.time(0,0,0)
        default_end_time = datetime.time(23,59,59)
        self.df = self.df[(self.df['Time'] >= default_start_time) & (self.df['Time'] <= default_end_time)]

        if trigger_error:
            self.c1_date.write(f'<div style="{style_markdown_error}">There is no data. Start time set to {default_start_time} and end time set to {default_end_time}. </div>', unsafe_allow_html=True)
            self.c2_date.write(f'<div style="{style_markdown_warning}">Verify if START TIME is greater than END TIME.</div>', unsafe_allow_html=True)
    
    def apply_farm_filter(self, options, refer_column):
        self.df = self.df[self.df[refer_column].isin(options)]
    
    def apply_plm_filter(self, options, refer_column):
        self.df = self.df[self.df[refer_column].isin(options)]
    
    def apply_deveui_filter(self, options, refer_column):
        self.df = self.df[self.df[refer_column].isin(options)]

    def return_data_frame(self):
        return self.df
    
    def apply_battery_filter(self, bat_min, bat_max):
        self.df = self.df[(self.df.battery >= bat_min) & (self.df.battery <= bat_max)]
    
    def apply_race_filter(self, options, refer_column):
        self.df = self.df[self.df[refer_column].isin(options)]

    def apply_message_filter(self, min_qtd, max_qtd):
        self.df = self.df[(self.df['Sent Messages'] >= min_qtd) & (self.df['Sent Messages'] <= max_qtd)]

    def get_unique_options(self, refer_column):
        return self.df[refer_column].unique()
    

class BuildFilterForms:
    def __init__(self, data_frame):
        self.df = data_frame
        self.c1_date, self.c2_date = st.columns(2)

    def build_date_filter(self):
        c1_date, c2_date = st.columns(2)
        inicio = c1_date.date_input(label='Start date:', max_value=datetime.datetime.now(tz=pytz.timezone('Brazil/East')), min_value=self.df['payloaddatetime'].min(),
                        key='data_inicio', value=datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - datetime.timedelta(days=1))
        fim = c2_date.date_input(label='End date:', min_value=self.df['CreatedAt'].min(), max_value=self.df['payloaddatetime'].max() + datetime.timedelta(days=1),
                    key='data_fim', value=datetime.datetime.now(tz=pytz.timezone('Brazil/East')) + datetime.timedelta(days=1))
        
    def build_plm_filter(self):
        total_opcs= self.df['PLM'].unique()
        plm_filter_options = st.multiselect(label='Choose any PLM', options=total_opcs, key='plm_alternative')
        return plm_filter_options