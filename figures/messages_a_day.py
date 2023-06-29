import plotly.express as px
from .update_fig_elements import alter_hover

def messages_a_day(data, date_period):
    fig = px.bar(data_frame=data, x='PLM', y='Sent Messages', color='Sent Messages', color_continuous_scale=px.colors.sequential.Plotly3_r, height=500,
                 text_auto=True)
    
    start_day, end_day = [date_period[0].day, date_period[1].day]
    start_month, end_month = [date_period[0].month, date_period[1].month]
    start_year, end_year = [date_period[0].year, date_period[1].year]
    
    fig.update_layout(title=dict(text=f'Sent messages from {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day}', 
                                 font=dict(size=25, family='roboto'), x=0.5, y=0.96, yanchor='top', xanchor='center'), font_family='roboto', template='plotly',
                                 coloraxis_colorbar=dict(title='Qty of messages', thickness=35, ticks='outside', y=0.9, yanchor='top'))
    fig.update_xaxes(showticklabels=False, visible=False)
    fig.update_yaxes(title=dict(text='Messages a day', font=dict(size=18, family='roboto')), showticklabels=False)

    fig.update_traces(textfont_size=15, textposition='outside')
    alter_hover(fig)
    return fig