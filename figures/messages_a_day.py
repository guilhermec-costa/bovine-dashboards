import plotly.express as px

def messages_a_day(data):
    fig = px.bar(data_frame=data, x='PLM', y='Id', color='Id', color_continuous_scale=px.colors.sequential.Plotly3_r, height=550,
                 text_auto=True)
    
    fig.update_layout(title=dict(text='Sent messages', font=dict(size=25), x=0.5, y=0.93, yanchor='top', xanchor='center'))
    fig.update_xaxes(title=dict(text=None))
    fig.update_yaxes(title=dict(text='Messages a day', font=dict(size=16)))

    fig.update_traces(textfont_size=12, textposition='outside')
    fig.update_coloraxes(showscale=False)
    return fig