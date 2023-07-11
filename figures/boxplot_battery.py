import plotly.graph_objects as go
from . import update_fig_elements
import numpy as np
import streamlit as st
import datetime

def style_annotations(fig):
    fig.update_annotations(font=dict(family='roboto', size=16, color='white'), arrowcolor='#FF890C',
                           arrowsize=2, arrowwidth=2, arrowhead=2,
                           bordercolor='#B7A2FF', 
                        opacity=1, borderwidth=2, bgcolor='#430CFF')

def boxplot_battery(data, point_dist, enable_annotations):
    fig = go.Figure()
    greater_date_filtered = data[data['payloaddatetime'] >= data['payloaddatetime'].max()]
    q1, q2, q3 = np.quantile(greater_date_filtered['battery'], np.arange(0.25, 1, 0.25))
    std = np.std(greater_date_filtered['battery'])
    mean = np.mean(greater_date_filtered['battery'])
    min_value = np.min(greater_date_filtered['battery'])
    iqr = q3 - q1
    lower_fence = q1 - (1.5*iqr)
    boxpoints = 'all' if point_dist == 'inliers + outliers' else 'outliers'
    fig.add_trace(go.Box(x=data['payloaddatetime'], y=data['battery'], boxmean='sd', notched=False, line=dict(color='#71A3FA', width=2),
                         marker=dict(opacity=1, color='orange', outliercolor='red', size=7), jitter=0.3, boxpoints=boxpoints,
                         whiskerwidth=0.3, hoverinfo=['x+y+z+text+name'], hoveron='boxes+points', pointpos=0))
    
    fig.update_layout(height=850, title=dict(text='Battery boxplot distribution', font=dict(size=25, family='roboto'),
                                             xanchor='center', yanchor='top', x=0.5, y=0.93))
                                            #  paper_bgcolor='white', plot_bgcolor='white')
    fig.update_yaxes(tickfont=dict(size=16, family='roboto'), title=dict(text="Voltage", font=dict(size=18, family='roboto')), showline=True, linewidth=1, color='grey')
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1, color='grey')

    if enable_annotations:
        # fig.update_traces(pointpos=-1.3)
        fig.add_annotation(x=data['payloaddatetime'].max(), y=q3, text='3d quartile', ax=180, ay=0, showarrow=True, align='left')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=q1, text='1st quartile', ax=180, ay=0, yanchor='top', showarrow=True, align='left')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=q2, text='Median', ax=180, ay=0, yanchor='top', showarrow=True, yref='y')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=mean, text='Mean', ax=-180, ay=0, yanchor='top', showarrow=True, yref='y')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=mean + std, text='mean + standard deviation', ax=-180, ay=0, showarrow=True, yref='y')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=mean - std, text='mean - standard deviation', ax=180, ay=0, showarrow=True, yref='y')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=mean - std, text='mean - standard deviation', ax=180, ay=0, showarrow=True, yref='y')
        fig.add_annotation(x=data['payloaddatetime'].max(), y=min_value, text='Min value level', ax=180, ay=0, showarrow=True, yref='y')
        style_annotations(fig=fig) 
    update_fig_elements.alter_hover(fig)

    return fig