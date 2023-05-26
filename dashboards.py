import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import modulos
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters, FilterOptions

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
    

def convert_to_timestamp(df, column:str):
    df[column] = df[column].apply(lambda x: datetime.strptime(str(x), '%Y-%m-%dT%H:%M:%S.%f%z'))
    

content = run_query('SELECT * FROM public."bovinedashboard";')
columns_name = run_query("""
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'public' AND table_name   = 'bovinedashboard';
""")

colunas = [x[0] for x in columns_name]
df = pd.DataFrame(content, columns=colunas)
vw_tab_aggrid = GridBuilder(df, key='filtered_df.df')
tab_formatada, bovine_data = vw_tab_aggrid.grid_builder()

# Conversão de datas para o formato timestamp do banco
convert_to_timestamp(bovine_data, 'payloaddatetime')
convert_to_timestamp(bovine_data, 'LastCommunication')
convert_to_timestamp(bovine_data, 'CreatedAt')

# leitura dos dados
bovine_data.dropna(axis=0, how='any', inplace=True)

c1, c2 = st.columns(2)
filtered_df = Filters(data_frame=bovine_data)

# filtro de datas
inicio = c1.date_input(label='Data de ínicio:', min_value=filtered_df.df['CreatedAt'].min() + timedelta(days=-1),
                        key='data_inicio', value=filtered_df.df['CreatedAt'].min() + timedelta(days=-1))
fim = c2.date_input(label='Data de fim:', min_value=filtered_df.df['CreatedAt'].min(), 
                    key='data_fim', value=datetime.now() + timedelta(days=1))

inicio = pd.to_datetime(inicio, utc=True)
fim = pd.to_datetime(fim, utc=True)

filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime')


c1__farm, c2_plm, c3_deveui = st.columns(3)
farm_filter_opcs = c1__farm.multiselect(label='Filtro de fazenda', options=filtered_df.df['Name'].unique())
if len(farm_filter_opcs) == 0:
    pass


plm_filter_options = c2_plm.multiselect(label='Filtro de PLM"s', options=filtered_df.df['PLM'].unique())
deveui_filter_options = c3_deveui.multiselect(label='Filtro de DevEUI', options=filtered_df.df['Identifier'].unique())

if len(plm_filter_options) >= 1: # precisa ser outro if
    filtered_df.apply_plm_filter(options=plm_filter_options)

# if len(deveui_filter_options) >= 1:
#     st.write(deveui_filter_options)
#     filtered_df.apply_deveui_filter(options=deveui_filter_options)


# Função que multiplica por 1000 os valores menores que 100.
filtered_df.df['battery'] = filtered_df.df['battery'].apply(lambda x: modulos.multiplica(x))
minimo = int(filtered_df.df['battery'].min())
maximo = int(filtered_df.df['battery'].max())


slider_bateria = st.slider(label='Range de bateria', value=[minimo, maximo], min_value=minimo,max_value=maximo)                  

# Função que filtra os dispostivos conforme o range de bateria selecionado no slider
filtered_df.df = filtered_df.df[(filtered_df.df.battery >= slider_bateria[0]) & (filtered_df.df.battery <= slider_bateria[1])]

# Agrupamentos por PLM
agrupado = filtered_df.df.groupby(by='PLM')
fig = go.Figure()

# Inserção de uma linha no gráfico para cada agrupamento de PLM
for name, grupo in agrupado:
    grupo.sort_values(by='payloaddatetime', inplace=True)
    grupo = grupo[grupo['payloaddatetime'].dt.month > 4]
    fig.add_trace(go.Scatter(x=grupo['payloaddatetime'], y=grupo['battery'], 
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