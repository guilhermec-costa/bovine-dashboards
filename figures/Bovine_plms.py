import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend
import pandas as pd

def plot_scatter_plm(data, date_period, qtd):
    fig = go.Figure()
    for name, groups in data:
        groups.sort_values(by='payloaddatetime', inplace=True)
        groups = groups[groups['payloaddatetime'].dt.month > 4]
        fig.add_trace(go.Scatter(x=groups['payloaddatetime'], y=groups['battery'], 
                            mode="markers+lines", line_shape='spline', name=name, hovertemplate= f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Date: %{x}</br>' + 
                                                                                                '<i>Battery: %{y}</i>')
                )
    
    start_day, end_day = [date_period[0].day, date_period[1].day]
    start_month, end_month = [date_period[0].month, date_period[1].month]
    start_year, end_year = [date_period[0].year, date_period[1].year]

    fig.update_layout(height=600, title=dict(text=f'Battery level per bovine from {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day} - {qtd} bovines', xanchor='center',yanchor='top', 
                                        x=0.5, y=0.93, font=dict(size=25, family='roboto')
                                        ),
                    legend=dict(orientation='v'), template='plotly', font_family='roboto')
    
    fig.update_yaxes(tickfont=dict(size=16, family='roboto'), title=dict(text="Voltage", font=dict(size=18)))
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showgrid=True, griddash='dash')

    # alterando o design do cursor e da legenda
    alter_legend(fig=fig, title='PLM')
    alter_hover(fig=fig)

    return fig