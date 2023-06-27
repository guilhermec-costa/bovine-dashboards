import plotly.graph_objects as go
from . import update_fig_elements
import pandas as pd

def location_status_chart(data):
    fig = go.Figure()
    for name, groups in data:
            groups.sort_values(by='Date', inplace=True)
            fig.add_trace(go.Scatter(x=groups['Date'], y=groups['Status'], 
                                mode="markers", name=name, marker=dict(size=11), hovertemplate=f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Date: %{x}</br>' + 
                                                                                                '<i>Status: %{y}</i>'))

    fig.update_layout(height=500, title=dict(text='Location Status over time', font=dict(size=25), x=0.5,y=0.93, xanchor='center', yanchor='top'))   
    fig.update_yaxes(tickfont=dict(size=18), showgrid=False)
    fig.update_xaxes(showgrid=True, griddash='solid', showline=True, linewidth=1, color='gray', mirror=True,
                     tickfont=dict(size=16))
    
    update_fig_elements.alter_hover(fig)
    update_fig_elements.alter_legend(fig, title='PLM')
    return fig