import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='Dashboards Bois', layout='wide')

def alter_legend(fig):
    fig.update_layout(legend=dict(font=dict(size=13, color="white"), bgcolor="#051732",
                                  bordercolor="black", borderwidth=2, title=dict(text='PLM dos bois', font=dict(size=16))))
    
def alter_hover(fig, mode="closest"):
    fig.update_layout(hovermode=mode, hoverlabel=dict(bgcolor="AntiqueWhite", font_color="black",
                                                    font_size=14, bordercolor="blue"))

def multiplica(bateria):
    if bateria < 100:
        bateria *= 1000
    return bateria

conc = pd.read_excel('novo_concatenado.xlsx')
conc.dropna(axis=0, how='any', inplace=True)



conc['Data correta'] = conc['Data correta'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S'))

inicio = st.date_input(label='Data de ínicio:', min_value=conc['Data correta'].min(), key='data_inicio')
fim = st.date_input(label='Data de ínicio:', min_value=conc['Data correta'].min(), key='data_fim')

inicio = pd.to_datetime(inicio)
fim = pd.to_datetime(fim)
filtrado = conc[(conc['Data correta'] >= inicio) & (conc['Data correta'] <= fim)]

agrupado = filtrado.groupby(by='PLM')


fig = go.Figure()
for name, grupo in agrupado:
    grupo.sort_values(by='Data correta', inplace=True)
    grupo['BATERIA'] = grupo['BATERIA'].apply(lambda x: multiplica(x))
    grupo = grupo[grupo['Data correta'].dt.month > 4]
    fig.add_trace(go.Scatter(x=grupo['Data correta'], y=grupo['BATERIA'], 
                            mode="markers+lines", line_shape='spline', name=name, hovertemplate= f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Data: %{x}</br>' + 
                                                                                                '<i>Bateria: %{y}</i>',
                            ))
    # fig.add_trace(go.Scatter(x=grupo['Data correta'], y=grupo['BATERIA'], mode="markers+lines", line_shape='spline', legendgroup=name))
fig.update_layout(height=900, title=dict(text='Dashboards SpaceVis', xanchor='center',
                                                     yanchor='top', x=0.5, y=0.93, font=dict(size=25)))


fig.update_yaxes(tickfont=dict(size=16), title=dict(
        text="Bateria", font=dict(size=16)))

fig.update_xaxes(tickfont=dict(size=16), title=dict(font=dict(size=16)))


alter_legend(fig=fig)
alter_hover(fig=fig)


st.plotly_chart(fig, use_container_width=True)