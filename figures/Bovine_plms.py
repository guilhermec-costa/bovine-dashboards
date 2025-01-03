import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend
import numpy as np

def plot_scatter_plm(data, date_period, qtd, id_kind):
    fig = go.Figure()
    for name, groups in data:
        groups.sort_values(by='payloaddatetime', inplace=True)
        # groups = groups[groups['payloaddatetime'].dt.month > 4]
        fig.add_trace(go.Scatter(x=groups['payloaddatetime'], y=groups['battery'], 
                            mode="markers+lines", line_shape='spline', name=name, hovertemplate= f'<i>{id_kind}: {name}</i>' + 
                                                                                                '<br>Date: %{x}</br>' + 
                                                                                                '<i>Battery: %{y}<i>' +
                                                                                                f'<br>Weight: {np.mean(groups["Weight"])} Kg</br>' +
                                                                                                f'<i>Race: {groups["race_name"].unique()[0]}</i>')
                )
    
    start_day, end_day = [date_period[0].day, date_period[1].day]
    start_month, end_month = [date_period[0].month, date_period[1].month]
    start_year, end_year = [date_period[0].year, date_period[1].year]

    fig.update_layout(height=850, title=dict(text=f'Battery level per bovine from {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day} - {qtd} bovines', xanchor='center',yanchor='top', 
                                        x=0.5, y=0.93, font=dict(size=25, family='roboto')
                                        ),
                    legend=dict(orientation='v'), template='plotly', font_family='roboto')
    
    fig.update_yaxes(tickfont=dict(size=16, family='roboto'), title=dict(text="Voltage", font=dict(size=18)), showline=True, linewidth=1, color='grey')
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), showgrid=True, griddash='dash', showline=True, linewidth=1, color='grey')

    # alterando o design do cursor e da legenda
    alter_legend(fig=fig, title=id_kind)
    alter_hover(fig=fig)

    return fig