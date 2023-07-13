import plotly.express as px
from .update_fig_elements import alter_hover, alter_legend

def farm_chart(data):
    # colors = ['gold', 'darkorange']
    # fig = go.Figure(data=[go.Pie(labels=data.index, values=data[1])])
    fig = px.pie(data_frame=data, labels='Farm_name', values='Qtd', names='Farm_name', color_discrete_sequence=px.colors.qualitative.Alphabet,
                 hover_name='Farm_name', hover_data=['Qtd'])

    fig.update_traces(textinfo='percent', textfont_size=20, marker=dict(line=dict(color='#230166', width=1)))
    fig.update_layout(title=dict(text='Bovine per farm', font=dict(size=25, family='roboto'), yanchor='top', xanchor='center', x=0.5, y=0.97),
                      legend=dict(x=0.78, y=0.7, orientation='v'), font_family='roboto')

    alter_hover(fig)
    alter_legend(fig, title='Farms')

    return fig