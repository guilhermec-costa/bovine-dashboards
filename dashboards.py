import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters
from figures.Bovine_plms import plot_scatter_plm
import queries.bovine_query as bovn_q
from data_treatement.data_dealer import *

# configuração da página
st.set_page_config(page_title='Dashboards SpaceVis', layout='wide', page_icon=':bar_chart:')

@st.cache_resource
def start_connection():
    return pgsql.connect(**st.secrets['postgres'])

# Iniciando query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()    

conn = start_connection()
    
content = run_query(bovn_q.QUERY_BOVINE_DASHBOARD)
columns_name = run_query(bovn_q.COLUMNS_TO_DATAFRAME)
bovine_registers = run_query(bovn_q.BOVINE_NUMBER)[0][0]
battery_mean_last30days = float(run_query(bovn_q.BATTERY_MEAN_LAST_30DAYS)[0][0])
battery_mean_last24hours = float(run_query(bovn_q.BATTERY_MEAN_LAST_24HOURS)[0][0])
diff_last_day = round(battery_mean_last24hours - float(run_query(bovn_q.BATTERY_MEAN_LAST_48HOURS)[0][0]), 2)

colunas = [x[0] for x in columns_name]
df = pd.DataFrame(content, columns=colunas)
# df['payloaddatetime'] = df['payloaddatetime'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S%z'))

# Função que multiplica por 1000 os valores menores que 100.
df['battery'] = df['battery'].apply(lambda x: x * 1000 if x < 100 else x)

metric1, metric2, metric3, *_ = st.columns(4, gap='small')
with open('style.css', 'r') as style:
    st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)

    metric1.metric(label='Bois cadastrados', value=bovine_registers)
    metric2.metric(label='Média de bateria últimos 30 dias', value=battery_mean_last30days)
    metric3.metric(label='Bateria média últimas 24 horas', value=battery_mean_last24hours, 
                   delta=diff_last_day,
                   help='Comparação entre o nível de bateria da data atual com as últimas 48 horas.')
    st.markdown('---')

button1, button2, *_ = st.columns(8, gap='small')
update_database = button1.button(label='Atualizar base de dados', type='primary')
if update_database:
    st.experimental_rerun()

download_database = button2.download_button(label='Baixar tabela', data=df.to_csv(), file_name='novo_arquivo.csv',
                                            mime='text/csv')
    

vw_tab_aggrid = GridBuilder(df, key='filtered_df.df')
tab_formatada, bovine_data = vw_tab_aggrid.grid_builder()

# tratamento dos dados
convert_to_timestamp(bovine_data, 'payloaddatetime')
convert_to_timestamp(bovine_data, 'LastCommunication')
convert_to_timestamp(bovine_data, 'CreatedAt')
clear_rows(bovine_data)

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

c1__farm, c2_plm = st.columns(2)
farm_filter_opcs = c1__farm.multiselect(label='Filtro de fazenda', options=filtered_df.df['Name'].unique())
if len(farm_filter_opcs) == 0:
    pass
else:
    filtered_df.df = filtered_df.df[filtered_df.df['Name'].isin(farm_filter_opcs)]

plm_filter_options = c2_plm.multiselect(label='Filtro de PLM"s', options=filtered_df.df['PLM'].unique())
if len(plm_filter_options) >= 1: # precisa ser outro if
    filtered_df.apply_plm_filter(options=plm_filter_options)


minimo = int(filtered_df.df['battery'].min())
maximo = int(filtered_df.df['battery'].max())
slider_bateria = st.slider(label='Range de bateria', value=[minimo, maximo], min_value=minimo,max_value=maximo)

# Função que filtra os dispostivos conforme o range de bateria selecionado no slider
filtered_df.df = filtered_df.df[(filtered_df.df.battery >= slider_bateria[0]) & (filtered_df.df.battery <= slider_bateria[1])]

# Agrupamentos por PLM
agrupado = filtered_df.df.groupby(by='PLM')
bovine_chart = plot_scatter_plm(agrupado, date_period=[inicio, fim])


st.plotly_chart(bovine_chart, use_container_width=True)