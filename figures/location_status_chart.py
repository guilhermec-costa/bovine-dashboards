import plotly.graph_objects as go
import plotly.express as px
from . import update_fig_elements
import streamlit as st

def location_status_chart(data):
    fig = go.Figure()
    for name, groups in data:
            groups.sort_values(by='Date', inplace=True)
            fig.add_trace(go.Scatter(x=groups['Date'], y=groups['Status'], 
                                mode="markers", name=name, marker=dict(size=11), hovertemplate=f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Date: %{x}</br>' + 
                                                                                                '<i>Status: %{y}</i>'))

    fig.update_layout(height=500, title=dict(text='Location status over time (specific times)', font=dict(size=25, family='roboto'), x=0.5,y=0.93, xanchor='center', yanchor='top'),
                      template='plotly', font_family='roboto')   
    fig.update_yaxes(tickfont=dict(size=17), showgrid=False)
    fig.update_xaxes(showgrid=True, griddash='solid', showline=True, linewidth=1, color='gray', mirror=True,
                     tickfont=dict(size=16))
    
    update_fig_elements.alter_hover(fig)
    update_fig_elements.alter_legend(fig, title='PLM')
    return fig

def count_location_status(data, mode: str, columns_to_add, barmode='group'):
    fig = go.Figure()
    for column in columns_to_add:
        color = '#00D303' if column == 'Valid location' else '#DC1700'
        if mode == 'Only Bars':
            fig.add_trace(go.Bar(x=data.index, y=data[column], name=column,marker=dict(color=color), text=data[column], textposition='auto'))  
            fig.update_layout(barmode=barmode)
        elif mode == 'Only Lines':
            fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='markers+lines',name=column,marker=dict(color=color), line=dict(width=3, shape='linear'), text=data[column], textposition='top center'))
        else:
            if column == 'Invalid location':
                fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='markers+lines', name=column,marker=dict(color=color), line=dict(width=3, shape='linear'), text=data[column], textposition='top center'))
            else:
                fig.add_trace(go.Bar(x=data.index, y=data[column], name=column, marker=dict(color=color), text=data[column], textposition='auto'))

    fig.update_layout(height=500, title=dict(text='Location status over time', font=dict(size=25, family='roboto'), x=0.5,y=0.93, xanchor='center', yanchor='top'),
                    template='plotly', font_family='roboto', font=dict(size=16, family='roboto')) 
    fig.update_yaxes(tickfont=dict(size=16), showgrid=True)
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), tickvals=data.index, tickangle=30)

    fig.update_traces(hovertemplate='<i>Date: %{x}</i>' + 
                                    '<br>Quantity: %{y}</br>')
    update_fig_elements.alter_hover(fig, mode='x unified')
    update_fig_elements.alter_legend(fig, title='Status')
    return fig