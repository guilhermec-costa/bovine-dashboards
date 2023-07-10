import plotly.express as px

def boxplot_battery(data):
    fig = px.box(data, x='payloaddatetime', y='battery', points='all')
    return fig