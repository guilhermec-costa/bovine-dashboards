import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st
import modulos
import connection
import psycopg2 as pgsql

# configuração da página
st.set_page_config(page_title='Dashboards SpaceVis', layout='wide', page_icon=':bar_chart:')

@st.cache_resource
def start_connection():
    return pgsql.connect(**st.secrets['postgres'])

conn = start_connection()

# Iniciando query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    

content = run_query('SELECT * FROM public."viewdashboards";')
columns_name = run_query("""
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'public' AND table_name   = 'viewdashboards';
""")
#Comentário aleatório

colunas = [x[0] for x in columns_name]
df = pd.DataFrame(content, columns=colunas)
# df['LastCommunication'] = df['LastCommunication'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S%z'))
st.write(df)

# leitura dos dados
conc = df
# conc = pd.read_excel('novo_concatenado.xlsx')
conc.dropna(axis=0, how='any', inplace=True)


#conversão para datas
# conc['Data correta'] = conc['Data correta'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S'))

c1, c2 = st.columns(2)

# filtro de ddtas
inicio = c1.date_input(label='Data de ínicio:', min_value=conc['CreatedAt'].min(),
                        key='data_inicio', value=datetime(2023, 5, 14))
fim = c2.date_input(label='Data de fim:', min_value=conc['CreatedAt'].min(), 
                    key='data_fim', value=datetime.now())


# filtro de PLMs
filtro_plm = st.multiselect(label='Filtro de PLM"s', options=conc['PLM'].unique())

# verificando se há ou não PLM's filtradas. Caso não haja, o df é igual. Caso haja, o filtro é aplicado
if len(filtro_plm) == 0:
    filtrado_plm = conc
else:
    filtrado_plm = conc[conc['PLM'].isin(filtro_plm)]


# Função que multiplica por 1000 os valores menores que 100.
filtrado_plm['battery'] = filtrado_plm['battery'].apply(lambda x: modulos.multiplica(x))

minimo = int(filtrado_plm['battery'].min())
maximo = int(filtrado_plm['battery'].max())


slider_bateria = st.slider(label='Range de bateria', value=[minimo, maximo],
                                                    min_value=minimo,max_value=maximo
                        )

# Função que filtra os dispostivos conforme o range de bateria selecionado no slider
filtrado_plm = filtrado_plm[(filtrado_plm.battery >= slider_bateria[0]) & (filtrado_plm.battery <= slider_bateria[1])]

# Filtro de datas
inicio = pd.to_datetime(inicio, utc=True)
fim = pd.to_datetime(fim, utc=True)
filtrado = filtrado_plm[(filtrado_plm['LastCommunication'] >= inicio) & (filtrado_plm['LastCommunication'] <= fim)]

# Agrupamentos por PLM
agrupado = filtrado.groupby(by='PLM')
fig = go.Figure()

# Inserção de uma linha no gráfico para cada agrupamento de PLM
for name, grupo in agrupado:
    grupo.sort_values(by='LastCommunication', inplace=True)
    grupo = grupo[grupo['LastCommunication'].dt.month > 4]
    fig.add_trace(go.Scatter(x=grupo['LastCommunication'], y=grupo['battery'], 
                            mode="markers+lines", line_shape='spline', name=name, hovertemplate= f'<i>PLM: {name}</i>' + 
                                                                                                '<br>Data: %{x}</br>' + 
                                                                                                '<i>Bateria: %{y}</i>',
                            ))

fig.update_layout(height=900, title=dict(text='Dashboards SpaceVis', xanchor='center',yanchor='top', 
                                         x=0.5, y=0.93, font=dict(size=25)
                                    ))
fig.update_yaxes(tickfont=dict(size=16), title=dict(text="Bateria", font=dict(size=16)))
fig.update_xaxes(tickfont=dict(size=16), title=dict(font=dict(size=16)))

# alterando o design do cursor e da legenda
modulos.alter_legend(fig=fig)
modulos.alter_hover(fig=fig)

st.plotly_chart(fig, use_container_width=True)