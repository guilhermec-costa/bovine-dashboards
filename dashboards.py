import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters
from figures import Bovine_plms, pie_chart_farm, pie_chart_race, battery_30days, messages_a_day
import queries.bovine_query as bovn_q
from data_treatement.data_dealer import *
from streamlit_extras.metric_cards import style_metric_cards
from authenticator import login_authenticator
from streamlit_extras.toggle_switch import st_toggle_switch
from streamlit_lottie import st_lottie
import requests
import lottie_loader

# # configuração da página
# with open('style.css') as file:
#         st.markdown(f'<style>{file.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='wide', page_title='Dashboards SpaceVis')
def start_app(user):
    st.session_state.new_user = False
    *_, add_user, logout_position = st.columns(12)

    with logout_position:
        logout = login_authenticator.logout('Logout', 'main')
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
    bovine_per_farm = pd.DataFrame(run_query(bovn_q.BOVINE_PER_FARM), columns=['Farm_name', 'Qtd'])
    bovine_per_race = pd.DataFrame(run_query(bovn_q.BOVINE_PER_RACE), columns=['Race_name', 'Qtd'])
    battery_metrics_30days = pd.DataFrame(run_query(bovn_q.BATTERY_METRICS_30DAYS), columns=['Date', 'Mean', 'Max', 'Min'])
    diff_last_day = round(battery_mean_last24hours - battery_mean_last48hours, 2)
    
    farm_chart = pie_chart_farm.farm_chart(data=bovine_per_farm)
    race_chart = pie_chart_race.race_chart(data=bovine_per_race)
    battery_chart = battery_30days.line_battery_chart(data=battery_metrics_30days)

    colunas = [x[0] for x in columns_name]
    df = pd.DataFrame(content, columns=colunas)

    # Função que multiplica por 1000 os valores menores que 100.
    df['battery'] = df['battery'].apply(lambda x: x / 1000 if x > 100 else x)

    metric1, metric2, metric3, *_ = st.columns(4, gap='small')
    metric1.metric(label='Active bovines', value=bovine_registers, delta=f'')
    metric2.metric(label='Medium battery on last 30 days', value=f'{battery_mean_last_month}V')
    metric3.metric(label='last 24 hours battery perfomance', value=f'{battery_mean_last24hours}V', 
                    delta=diff_last_day,
                    help='last 24 hours battery performance in comparison with the 48 last hours battery perfomance')
    style_metric_cards(background_color='#6D23FF', border_size_px=1.5, 
                    border_color='#39275B', border_radius_px=25, border_left_color='#39275B')
    # st.divider()

    with st.expander(label='Visual charts'):
        c1_expand, c2_expand, c3_expand = st.columns(3)
        c1_expand.plotly_chart(farm_chart)
        c2_expand.plotly_chart(race_chart)
        c3_expand.plotly_chart(battery_chart)

    *_, download_btn = st.columns(12, gap='small')
    download_database = download_btn.download_button(label='Download data', data=df.to_csv(), file_name='novo_arquivo.csv',
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

    c1__farm, c2_plm, c3_race = st.columns(3)
    
    farm_filter_opcs = c1__farm.multiselect(label='Choose a farm', options=filtered_df.df['Name'].unique())
    if len(farm_filter_opcs) >= 1:
        filtered_df.apply_farm_filter(options=farm_filter_opcs)
    
    race_filter_options = c3_race.multiselect(label='Choose a race', options=filtered_df.df['race_name'].unique())
    if len(race_filter_options) >= 1:
        filtered_df.apply_race_filter(options=race_filter_options)

    plm_filter_options = c2_plm.multiselect(label='Choose any PLM', options=filtered_df.df['PLM'].unique())
    if len(plm_filter_options) >= 1: # precisa ser outro if
        filtered_df.apply_plm_filter(options=plm_filter_options)

    min_battery = float(filtered_df.df['battery'].min())
    max_battery = float(filtered_df.df['battery'].max())
    min_bat, max_bat = st.slider(label='Battery range', value=[min_battery, max_battery], 
                            min_value=min_battery,max_value=max_battery)

    # Função que filtra os dispostivos conforme o range de bateria selecionado no slider
    filtered_df.apply_battery_filter(bat_min=min_bat, bat_max=max_bat)
    messages_per_day = filtered_df.df.groupby(by='PLM').count().reset_index()
    messages_per_day.rename(columns={'Id':'Sent Messages'}, inplace=True)
    messages_chart = messages_a_day.messages_a_day(data=messages_per_day, date_period=[inicio, fim])

    # Agrupamentos por PLM
    agrupado = filtered_df.df.groupby(by='PLM')
    bovine_chart = Bovine_plms.plot_scatter_plm(agrupado, date_period=[inicio, fim])

    c_switch, days_messages, *_ = st.columns(5)
    with c_switch:
        switch = st_toggle_switch(label='Messages per PLM', label_after=True, active_color='#11567f', inactive_color='#D3D3D3')
    if not switch:
        st.plotly_chart(bovine_chart, use_container_width=True)
    else:
        st.plotly_chart(messages_chart, use_container_width=True)

def initialize_session_state():
    # Inicialize as chaves necessárias no st.session_state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = False

lottie = lottie_loader.load_lottieurl('https://assets7.lottiefiles.com/packages/lf20_puciaact.json')
accept = lottie_loader.load_lottieurl('https://assets3.lottiefiles.com/datafiles/uoZvuyyqr04CpMr/data.json')
cat = lottie_loader.load_lottieurl('https://assets8.lottiefiles.com/temp/lf20_QYm9j9.json')
    
if __name__ == '__main__':
    initialize_session_state()
    menu1, menu2, menu3 = st.columns(3)
    with open('style.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    with menu2:
        name, authentication_status, username = login_authenticator.login(form_name='Login', location='main')
    if authentication_status:
        start_app(user=username)
    elif authentication_status is None:
        with menu2:
            st_lottie(lottie, loop=True, quality='high', width=650, height=500)
            pass
    else:
        with menu2:
            st.error('Be sure your credentials are correct')

    
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)