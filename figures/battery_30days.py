import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend

def line_battery_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Mean'], name='Mean battery', mode='lines+markers', hovertemplate='%{y}V'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Max'], name='Max battery', mode='lines+markers', hovertemplate='%{y}V'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Min'], name='Min battery', mode='lines+markers', hovertemplate='%{y}V'))

    fig.update_layout(title=dict(text='Battery perfomance last 30 days', x=0.5, y=0.9, yanchor='top', xanchor='center', font=dict(size=25, family='roboto')),
                      template='presentation', height=400, font_family='roboto')
    
    fig.update_xaxes(tickvals=data['Date'], tickangle=30, tickfont=dict(size=14, family='roboto'), showgrid=True, griddash='dash')
    fig.update_yaxes(tickfont=dict(size=16, family='roboto'))

    
    alter_hover(fig, mode='x unified')
    alter_legend(fig, title='Metrics')
    return fig