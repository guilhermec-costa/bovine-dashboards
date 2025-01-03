import plotly.express as px
from .update_fig_elements import alter_hover, alter_legend

def race_chart(data):
    fig = px.pie(data_frame=data, labels='Race_name', values='Qtd', names='Race_name', color_discrete_sequence=px.colors.qualitative.Alphabet)

    fig.update_traces(textinfo='percent', textfont_size=20, marker=dict(line=dict(color='#230166', width=1)))
    fig.update_layout(title=dict(text='Bovine per race', font=dict(size=25, family='roboto'), yanchor='top', xanchor='center', x=0.45, y=0.97),
                      legend=dict(x=0.85, y=0.7, orientation='v'), font_family='roboto')

    alter_hover(fig)
    alter_legend(fig, title='Races')
    return fig