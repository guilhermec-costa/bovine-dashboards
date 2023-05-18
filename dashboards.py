import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='Dashboards Bois', layout='wide')

conc = pd.read_excel('novo_concatenado.xlsx')
conc.dropna(axis=0, how='any', inplace=True)


conc['Data correta'] = conc['Data correta'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S'))
agrupado = conc.groupby(by='PLM')


def multiplica(bateria):
    if bateria < 100:
        bateria *= 1000
    return bateria

fig = go.Figure()
for name, grupo in agrupado:
    grupo.sort_values(by='Data correta', inplace=True)
    grupo['BATERIA'] = grupo['BATERIA'].apply(lambda x: multiplica(x))
    grupo = grupo[grupo['Data correta'].dt.month > 4]
    fig.add_trace(go.Scatter(x=grupo['Data correta'], y=grupo['BATERIA'], mode="markers+lines", line_shape='spline', name=name))
    # fig.add_trace(go.Scatter(x=grupo['Data correta'], y=grupo['BATERIA'], mode="markers+lines", line_shape='spline', legendgroup=name))
fig.update_layout(width=2000, height=800, title=dict(text='Dashboards Spaceviz', xanchor='center',
                                                     yanchor='top', x=0.5, y=0.93, font=dict(size=18)))

fig.update_yaxes(tickfont=dict(size=16), title=dict(
        text="Bateria", font=dict(size=16)))


st.write('')
st.plotly_chart(fig, use_container_width=True)