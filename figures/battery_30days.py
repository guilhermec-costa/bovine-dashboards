import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend

def line_battery_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Mean'], name='Mean battery', mode='lines+markers', line=dict(color='#F9A303')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Max'], name='Max battery', mode='lines+markers', line=dict(color='#03F9BD')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Min'], name='Min battery', mode='lines+markers', line=dict(color='#BEA7E4')))

    fig.update_layout(title=dict(text='Battery perfomance last 30 days', x=0.5, y=0.9, yanchor='top', xanchor='center', font=dict(size=18)),
                      template='seaborn')
    
    fig.update_xaxes(tickvals=data['Date'], tickangle=30, tickfont=dict(size=14), showgrid=True, griddash='dash')

    
    alter_hover(fig, mode='x unified')
    alter_legend(fig, title='Metrics')
    return fig