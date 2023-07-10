import plotly.graph_objects as go
from . import update_fig_elements
import streamlit as st
import datetime

def boxplot_battery(data, point_dist):
    fig = go.Figure()
    st.write(data['payloaddatetime'].max())
    boxpoints = 'all' if point_dist == 'inliers + outliers' else 'outliers'
    fig.add_trace(go.Box(x=data['payloaddatetime'], y=data['battery'], boxmean='sd', notched=False, line=dict(color='#71A3FA', width=2),
                         marker=dict(opacity=1, color='orange', outliercolor='red', size=7), jitter=0.5, boxpoints=boxpoints,
                         whiskerwidth=0.3, hoverinfo=['x+y+z+text+name'], hoveron='boxes+points', pointpos=-1.8))
    
    fig.update_layout(height=850, title=dict(text='Battery boxplot distribution', font=dict(size=25, family='roboto'),
                                             xanchor='center', yanchor='top', x=0.5, y=0.93))
                                            #  paper_bgcolor='white', plot_bgcolor='white')
    fig.update_yaxes(tickfont=dict(size=16, family='roboto'), title=dict(text="Voltage", font=dict(size=18, family='roboto')), showline=True, linewidth=1, color='grey')
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1, color='grey')

    # fig.add_annotation(x=data['payloaddatetime'].max() + datetime.timedelta(hours=3), y=3.9, text='Olá mundo')
    update_fig_elements.alter_hover(fig)

    return fig