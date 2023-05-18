import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st
import modulos

st.set_page_config(page_title='Dashboards Bois', layout='wide')

conc = pd.read_excel('novo_concatenado.xlsx')
conc.dropna(axis=0, how='any', inplace=True)



conc['Data correta'] = conc['Data correta'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S'))

c1, c2 = st.columns(2)
inicio = c1.date_input(label='Data de ínicio:', min_value=conc['Data correta'].min(),
                        key='data_inicio', value=datetime(2023, 5, 1))
fim = c2.date_input(label='Data de fim:', min_value=conc['Data correta'].min(), 
                    key='data_fim', value=datetime.now())

filtro_plm = st.multiselect(label='Filtro de PLM"s', options=conc['PLM'].unique())
if len(filtro_plm) == 0:
    filtrado_plm = conc
else:
    filtrado_plm = conc[conc['PLM'].isin(filtro_plm)]

inicio = pd.to_datetime(inicio)
fim = pd.to_datetime(fim)
filtrado = filtrado_plm[(filtrado_plm['Data correta'] >= inicio) & (filtrado_plm['Data correta'] <= fim)]

agrupado = filtrado.groupby(by='PLM')


fig = go.Figure()
for name, grupo in agrupado:
    grupo.sort_values(by='Data correta', inplace=True)
    grupo['BATERIA'] = grupo['BATERIA'].apply(lambda x: modulos.multiplica(x))
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


modulos.alter_legend(fig=fig)
modulos.alter_hover(fig=fig)


st.plotly_chart(fig, use_container_width=True)