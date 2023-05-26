import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend
def plot_scatter_plm(data):
    fig = go.Figure()
    for name, groups in data:
        groups.sort_values(by='payloaddatetime', inplace=True)
        groups = groups[groups['payloaddatetime'].dt.month > 4]
        fig.add_trace(go.Scatter(x=groups['payloaddatetime'], y=groups['battery'], 
                            mode="markers+lines", line_shape='spline', name=name, hovertemplate= f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Data: %{x}</br>' + 
                                                                                                '<i>Bateria: %{y}</i>')
                )
        
    fig.update_layout(height=900, title=dict(text='Dashboards SpaceVis', xanchor='center',yanchor='top', 
                                        x=0.5, y=0.93, font=dict(size=25)
                                        ))
    fig.update_yaxes(tickfont=dict(size=16), title=dict(text="Bateria", font=dict(size=16)))
    fig.update_xaxes(tickfont=dict(size=16), title=dict(font=dict(size=16)))

    # alterando o design do cursor e da legenda
    alter_legend(fig=fig)
    alter_hover(fig=fig)

    return fig