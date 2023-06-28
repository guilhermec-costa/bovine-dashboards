import plotly.express as px
from .update_fig_elements import alter_hover, alter_legend
from datetime import datetime, timedelta
import pytz

def last_battery(data):
    fig = px.bar(data_frame=data, x='PLM', y='battery', color='battery', color_continuous_scale=px.colors.sequential.Plotly3_r, height=480)
    fig.update_layout(title=dict(text=f'Last Battery Indicator until {(datetime.now(tz=pytz.timezone("Brazil/East"))).strftime("%Y/%m/%d %H:%M:%S")}', x=0.5, y=0.93, yanchor='top', xanchor='center',
                                 font=dict(size=25, family='roboto')), font_family='roboto', template='plotly',
                                 coloraxis_colorbar=dict(title='Battery Voltage', ticksuffix='V', thickness=35, ticks='outside', y=0.9, yanchor='top'))

    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_yaxes(title=dict(text='Voltage', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    
    alter_hover(fig)
    return fig