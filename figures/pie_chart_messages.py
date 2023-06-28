import plotly.express as px
from . import update_fig_elements

def pie_chart_messages(data):
    fig = px.pie(data_frame=data, labels='Moment', values='Qtd', names='Moment', color_discrete_sequence=px.colors.qualitative.Bold)

    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20, marker=dict(line=dict(color='#230166', width=1)), textposition='auto')
    fig.update_layout(title=dict(text='Devices sending messages according to date ranges', font=dict(size=25, family='roboto'), yanchor='top', xanchor='center', x=0.5, y=0.97),
                      legend=dict(x=0.78, y=0.7, orientation='v'), font_family='roboto')
    
    update_fig_elements.alter_hover(fig)
    update_fig_elements.alter_legend(fig, title='Date ranges')

    return fig
