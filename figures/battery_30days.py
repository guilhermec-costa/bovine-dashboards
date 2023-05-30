import plotly.graph_objects as go
from .update_fig_elements import alter_hover, alter_legend

def line_battery_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Mean'], name='Mean battery'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Max'], name='Max battery'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Min'], name='Min battery'))

    fig.update_layout(title=dict(text='Battery perfomance last 30 days', x=0.5, y=0.9, yanchor='top', xanchor='center', font=dict(size=18)),
                      template='seaborn')
    
    alter_hover(fig, mode='x unified')
    alter_legend(fig, title='Metrics')
    return fig