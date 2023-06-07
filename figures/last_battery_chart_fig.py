import plotly.express as px
from .update_fig_elements import alter_hover, alter_legend
from datetime import datetime

def last_battery(data):
    fig = px.bar(data_frame=data, x='PLM', y='battery', color='battery', color_continuous_scale=px.colors.sequential.Plotly3_r, height=480)
    fig.update_layout(title=dict(text=f'Last Battery Indicator until {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}', x=0.5, y=0.93, yanchor='top', xanchor='center',
                                 font=dict(size=18)))

    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_yaxes(title=dict(text='Voltage', font=dict(size=16)), showticklabels=False)
    
    alter_hover(fig)
    alter_legend(fig, title='Battery')
    return fig