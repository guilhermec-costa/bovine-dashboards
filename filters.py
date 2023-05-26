import pandas as pd
import streamlit as st

class Filters:
    def __init__(self, data_frame):
        self.df = data_frame

    def apply_date_filter(self, start, end, refer_column:str):
        self.df = self.df[(self.df[refer_column] >= start) & (self.df[refer_column] <= end)]
    
    def apply_farm_filter(self, options):
        self.df = self.df[self.df['Name'].isin(options)]
    
    def apply_plm_filter(self, options):
        self.df = self.df[self.df['PLM'].isin(options)]
    
    def apply_deveui_filter(self, options):
        self.df = self.df[self.df['Identifier'].isin(options)]

    def return_data_frame(self):
        return self.df

class FilterOptions(Filters):
   def return_filter_opcs(self):
        plm_filter_options = self.return_data_frame()['PLM'].unique()
        deveui_filter_options = self.return_data_frame()['Identifier'].unique()
        return plm_filter_options, deveui_filter_options
