import pandas as pd
import streamlit as st
import datetime
import pytz

class Filters:
    def __init__(self, data_frame):
        self.df = data_frame

    def apply_date_filter(self, start, end, refer_column:str, trigger_error=False):
        if start <= end:
            self.df = self.df[(self.df[refer_column] >= start) & (self.df[refer_column] <= end)]
        else:
            self.df = self.df[(self.df[refer_column] >= (datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - datetime.timedelta(days=1))) &
                               (self.df[refer_column] <= datetime.datetime.now(tz=pytz.timezone('Brazil/East')) + datetime.timedelta(days=1))]
            if trigger_error:
                st.error('There is no data. The filters were not applied.')
    
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

class FilterOptions(Filters):
   def return_filter_opcs(self):
        plm_filter_options = self.return_data_frame()['PLM'].unique()
        deveui_filter_options = self.return_data_frame()['Identifier'].unique()
        return plm_filter_options, deveui_filter_options
