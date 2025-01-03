import plotly.express as px
from .update_fig_elements import alter_hover, alter_legend
import plotly.graph_objects as go

def battery_categories(data):
    fig = go.Figure(data=[go.Pie(labels=data['Category'], values=data['Quantity'], hole=.5, marker=dict(colors=px.colors.qualitative.Alphabet))])
    # fig = px.pie(data_frame=data, labels='Category', values='Quantity', names='Category', color_discrete_sequence=px.colors.qualitative.Alphabet)

    fig.update_traces(textinfo='percent', textfont_size=20, marker=dict(line=dict(color='#230166', width=1)))
    fig.update_layout(title=dict(text='Battery categories by volt ranges', font=dict(size=25, family='roboto'), yanchor='top', xanchor='center', x=0.43, y=0.97),
                      legend=dict(x=0.78, y=0.7, orientation='v'), font_family='roboto')

    alter_hover(fig)
    alter_legend(fig, title='Battery ranges')
    return fig