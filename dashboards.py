import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters
from figures.Bovine_plms import plot_scatter_plm
import queries.bovine_query as bovn_q
from data_treatement.data_dealer import *
from streamlit_extras.metric_cards import style_metric_cards
from login_user import start_login

# configuração da página

def start_app(login_object, user):
    st.set_page_config(layout='wide')
    *_, logout = st.columns(12)
    with logout:
        logout = login_object.logout('Logout', 'main')
    st.success(f'Your welcome {user.capitalize()}!')
    st.markdown('###')

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
    battery_mean_last_month = float(run_query(bovn_q.BATTERY_MEAN_LAST_30DAYS)[0][0])
    try:
        battery_mean_last_2month = float(run_query(bovn_q.BATTERY_MEAN_LAST_60DAYS)[0][0])
        diff_last_month = round(battery_mean_last_month - battery_mean_last_2month, 2)
    except:
        pass
    battery_mean_last24hours = float(run_query(bovn_q.BATTERY_MEAN_LAST_24HOURS)[0][0])
    battery_mean_last48hours = float(run_query(bovn_q.BATTERY_MEAN_LAST_48HOURS)[0][0])
    diff_last_day = round(battery_mean_last24hours - battery_mean_last48hours, 2)

    colunas = [x[0] for x in columns_name]
    df = pd.DataFrame(content, columns=colunas)

    # Função que multiplica por 1000 os valores menores que 100.
    df['battery'] = df['battery'].apply(lambda x: x * 1000 if x < 100 else x)

    metric1, metric2, metric3, *_ = st.columns(4, gap='small')
    metric1.metric(label='Registred bovines', value=bovine_registers)
    metric2.metric(label='Medium battery on last 30 days', value=battery_mean_last_month)
    metric3.metric(label='last 24 hours battery perfomance',
                    value=battery_mean_last24hours, 
                    delta=diff_last_day,
                    help='last 24 hours battery performance in comparison with the 48 last hours battery perfomance')
    style_metric_cards(background_color='#6D23FF', border_size_px=1.5, 
                    border_color='#39275B', border_radius_px=25, border_left_color='#39275B')
    # st.divider()

    button1, button2, *_ = st.columns(8, gap='small')
    update_database = button1.button(label='Update database', type='primary')

    download_database = button2.download_button(label='Download data', data=df.to_csv(), file_name='novo_arquivo.csv',
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
    inicio = c1.date_input(label='Start date:', max_value=datetime.now(),
                            key='data_inicio', value=filtered_df.df['CreatedAt'].min() + timedelta(days=-1))
    fim = c2.date_input(label='End date:', min_value=filtered_df.df['CreatedAt'].min(), 
                        key='data_fim', value=datetime.now() + timedelta(days=1))

    inicio = pd.to_datetime(inicio, utc=True)
    fim = pd.to_datetime(fim, utc=True)

    filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime')

    c1__farm, c2_plm = st.columns(2)
    farm_filter_opcs = c1__farm.multiselect(label='Choose a farm', options=filtered_df.df['Name'].unique())
    if len(farm_filter_opcs) == 0:
        pass
    else:
        filtered_df.apply_farm_filter(options=farm_filter_opcs)

    plm_filter_options = c2_plm.multiselect(label='Choose any PLM', options=filtered_df.df['PLM'].unique())
    if len(plm_filter_options) >= 1: # precisa ser outro if
        filtered_df.apply_plm_filter(options=plm_filter_options)

    min_battery = int(filtered_df.df['battery'].min())
    max_battery = int(filtered_df.df['battery'].max())
    min_bat, max_bat = st.slider(label='Battery range', value=[min_battery, max_battery], 
                            min_value=min_battery,max_value=max_battery)


    # Função que filtra os dispostivos conforme o range de bateria selecionado no slider
    filtered_df.apply_battery_filter(bat_min=min_bat, bat_max=max_bat)

    # Agrupamentos por PLM
    agrupado = filtered_df.df.groupby(by='PLM')
    bovine_chart = plot_scatter_plm(agrupado, date_period=[inicio, fim])

    st.plotly_chart(bovine_chart, use_container_width=True)

try:
    login, login_object, username = start_login()
    if login:
        start_app(login_object=login_object, user=username)
except:
    pass