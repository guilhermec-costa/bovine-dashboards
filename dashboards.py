import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters
from figures import (Bovine_plms, pie_chart_farm, pie_chart_race, battery_30days, location_status_chart,
                    messages_a_day, last_battery_chart_fig, battery_categories, pie_chart_messages)
import queries.bovine_query as bovn_q
from data_treatement.data_dealer import *
from streamlit_extras.metric_cards import style_metric_cards
from authenticator import login_authenticator
from streamlit_extras.toggle_switch import st_toggle_switch
import lottie_loader
from datetime import datetime, timedelta
import pytz
from streamlit_lottie import st_lottie

    
streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"]  {
    font-family: 'Roboto', sans-serif;
    }
    </style>
"""

welcome = lottie_loader.load_lottieurl('https://assets7.lottiefiles.com/packages/lf20_xnbikipz.json')
limit_24h = datetime.now(tz=pytz.timezone('Brazil/East')) - timedelta(days=1)
limit_48h = datetime.now(tz=pytz.timezone('Brazil/East')) - timedelta(days=2)
limit_5days = datetime.now(tz=pytz.timezone('Brazil/East')) - timedelta(days=5)

@st.cache_resource
def start_connection():
    try:
        return pgsql.connect(**st.secrets['postgres'])
    except:
        st.error('Failed to connect to database.')
        return False

# Iniciando query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

st.cache_data(ttl=600)
def run_queries():
    global content, bovine_per_farm, bovine_per_race, battery_mean_last24hours, battery_mean_last48hours, battery_metrics_30days, \
    columns_name, bovine_registers, battery_mean_last24hours, battery_mean_last_month, diff_last_day, last_battery_data, volts_categories, location_status_data
    content = run_query(bovn_q.QUERY_BOVINE_DASHBOARD)
    columns_name = run_query(bovn_q.COLUMNS_TO_DATAFRAME)
    bovine_registers = run_query(bovn_q.BOVINE_NUMBER)[0][0]
    battery_mean_last_month = float(run_query(bovn_q.BATTERY_MEAN_LAST_30DAYS)[0][0])
    battery_mean_last24hours = float(run_query(bovn_q.BATTERY_MEAN_LAST_24HOURS)[0][0])
    battery_mean_last48hours = float(run_query(bovn_q.BATTERY_MEAN_LAST_48HOURS)[0][0])
    bovine_per_farm = pd.DataFrame(run_query(bovn_q.BOVINE_PER_FARM), columns=['Farm_name', 'Qtd'])
    bovine_per_race = pd.DataFrame(run_query(bovn_q.BOVINE_PER_RACE), columns=['Race_name', 'Qtd'])
    last_battery_data = pd.DataFrame(run_query(bovn_q.LAST_BATTERY_QUERY), columns=['PLM', 'payloaddatetime', 'battery'])
    battery_metrics_30days = pd.DataFrame(run_query(bovn_q.BATTERY_METRICS_30DAYS), columns=['Date', 'Mean', 'Max', 'Min'])
    diff_last_day = round(battery_mean_last24hours - battery_mean_last48hours, 2)
    volts_categories = pd.DataFrame(run_query(bovn_q.BATTERY_CATEGORIES), columns=['Category', 'Quantity'])
    location_status_data = pd.DataFrame(run_query(bovn_q.LOCATION_STATUS), columns=['PLM', 'Status', 'Date', 'race_Name', 'farm_name'])

def initialize_session_state():
    # Inicializando as chaves necessárias no st.session_state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = False

def start_app(user):
    st.session_state.new_user = False
    st.session_state.logout = False
    st.session_state.apply_filters_button = False
    *_, logout_position = st.columns(12)

    with logout_position:
        logout = login_authenticator.logout('Logout', 'main')
        st.session_state.logout = True
    st.success(f'Your welcome {user.capitalize()}!')
    st.markdown('###')
    
    farm_chart = pie_chart_farm.farm_chart(data=bovine_per_farm)
    race_chart = pie_chart_race.race_chart(data=bovine_per_race)
    volt_ranges = battery_categories.battery_categories(data=volts_categories)
    battery_chart = battery_30days.line_battery_chart(data=battery_metrics_30days)
    location_status_data['Date'] = location_status_data['Date'].apply(lambda x: x if str(x) != '0001-01-01 00:00:00+00:00' else datetime.now(tz=pytz.timezone('Brazil/East')))

    location_status_data['Date'] = pd.to_datetime(location_status_data['Date'], utc=True, errors='coerce')
    location_status_data['Status'] = location_status_data['Status'].apply(lambda x: 'Valid location' if x else 'Invalid location')

    colunas = [x[0] for x in columns_name]
    df = pd.DataFrame(content, columns=colunas)
    df['payloaddatetime'] = pd.to_datetime(df['payloaddatetime'], utc=True)


    # Função que multiplica por 1000 os valores menores que 100 na voltagem.
    df['battery'] = df['battery'].apply(lambda x: x / 1000 if x > 100 else x)

    filtered_24h = df[df['payloaddatetime'] >= limit_24h]
    filtered_48h = df[(df['payloaddatetime'] >= limit_48h) & (~df['PLM'].isin(filtered_24h['PLM']))]
    filtered_5days = df[(df['payloaddatetime'] >= limit_5days) & (~df['PLM'].isin(filtered_48h['PLM'])) & (~df['PLM'].isin(filtered_24h['PLM']))]
    filtered_5days_more = df[(df['payloaddatetime'] < limit_5days) & ((~df['PLM'].isin(filtered_48h['PLM']))
                                                                    & (~df['PLM'].isin(filtered_24h['PLM']))
                                                                    & (~df['PLM'].isin(filtered_5days)))]

    values_limits = [len(filtered_24h['PLM'].unique()), len(filtered_48h['PLM'].unique()), len(filtered_5days['PLM'].unique()), len(filtered_5days_more['PLM'].unique())]
    df_limits = pd.DataFrame({'Qtd':values_limits}, index=['Sent messages last 24 hours', 'Sent messages last 48 hours', 'Sent messages last 5 days', 
                                                           'Sent messages last 5+ days']).reset_index().rename(columns={'index':'Moment'})
    
    pie_chart_limits = pie_chart_messages.pie_chart_messages(data=df_limits)
    metric1, metric2, metric3, *_ = st.columns(4, gap='medium')
    metric1.metric(label='Active bovines', value=bovine_registers)
    metric2.metric(label='Medium battery on last 30 days', value=f'{battery_mean_last_month}V')
    metric3.metric(label='last 24 hours battery perfomance', value=f'{battery_mean_last24hours}V', 
                    delta=diff_last_day,
                    help='last 24 hours battery performance in comparison with the 48 last hours battery perfomance')
    style_metric_cards(background_color='#6D23FF', border_size_px=1.5, 
                    border_color='#39275B', border_radius_px=25, border_left_color='#39275B')

    with st.expander(label='Battery perfomance'):
        st.plotly_chart(battery_chart, use_container_width=True)
        st.markdown('---')
        c1_expand_battery, c2_expand_battery = st.columns(2, gap='small')
        c1_expand_battery.plotly_chart(volt_ranges, use_container_width=True)
        c2_expand_battery.plotly_chart(pie_chart_limits, use_container_width=True)

    with st.expander(label='General metrics'):
        c1_expand, c2_expand = st.columns(2)
        c1_expand.plotly_chart(farm_chart, use_container_width=True)
        c2_expand.plotly_chart(race_chart, use_container_width=True)

    *_, download_btn = st.columns(12, gap='small')

    download_database = download_btn.download_button(label='Download data', data=df.to_csv(), file_name='novo_arquivo.csv',
                                                mime='text/csv', key='download_btn')
    
    vw_tab_aggrid = GridBuilder(df, key='filtered_df.df')
    tab_formatada, bovine_data = vw_tab_aggrid.grid_builder()
    
    clear_rows(bovine_data)

    filtered_df = Filters(data_frame=bovine_data)
    filtered_status_loc = Filters(data_frame=location_status_data)

    filtered_status_loc.df['Date'] = pd.to_datetime(filtered_status_loc.df.Date)
    filtered_df.df['payloaddatetime'] = pd.to_datetime(filtered_df.df.payloaddatetime)
    filtered_df.df['CreatedAt'] = pd.to_datetime(filtered_df.df.CreatedAt)

    # filtro de datas
    with st.form(key='filters'):
        c1, c2 = st.columns(2)
        inicio = c1.date_input(label='Start date:', max_value=datetime.now(tz=pytz.timezone('Brazil/East')), min_value=filtered_df.df['payloaddatetime'].min(),
                            key='data_inicio', value=datetime.now(tz=pytz.timezone('Brazil/East')) - timedelta(days=1))
        fim = c2.date_input(label='End date:', min_value=filtered_df.df['CreatedAt'].min(), max_value=filtered_df.df['payloaddatetime'].max() + timedelta(days=1),
                        key='data_fim', value=datetime.now(tz=pytz.timezone('Brazil/East')) + timedelta(days=1))

        inicio = datetime.combine(inicio, datetime.min.time(), tzinfo=pytz.timezone('Brazil/East'))
        fim = datetime.combine(fim, datetime.min.time(), tzinfo=pytz.timezone('Brazil/East'))

        c1__farm, c2_plm, c3_race = st.columns(3)
        
        farm_filter_opcs = c1__farm.multiselect(label='Choose a farm', options=filtered_df.df['Name'].unique())
        
        race_filter_options = c3_race.multiselect(label='Choose a race', options=filtered_df.df['race_name'].unique())
        plm_filter_options = c2_plm.multiselect(label='Choose any PLM', options=filtered_df.df['PLM'].unique())

        min_battery = float(filtered_df.df['battery'].min())
        max_battery = float(filtered_df.df['battery'].max())
        min_bat, max_bat = st.slider(label='Battery range', value=[min_battery, max_battery], 
                                min_value=min_battery,max_value=max_battery, step=0.05, help='Only can be applied to the battery level per bovine figure.')

        if st.form_submit_button(label='Apply filters'):
            st.session_state.apply_filters_button = True
            filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime', trigger_error=True)
            filtered_status_loc.apply_date_filter(start=inicio, end=fim, refer_column='Date')
            if len(plm_filter_options) >= 1: 
                filtered_df.apply_plm_filter(options=plm_filter_options, refer_column='PLM')
                filtered_status_loc.apply_plm_filter(options=plm_filter_options, refer_column='PLM')
            if len(race_filter_options) >= 1:
                filtered_df.apply_race_filter(options=race_filter_options, refer_column='race_name')
                filtered_status_loc.apply_race_filter(options=race_filter_options, refer_column='race_Name')
            if len(farm_filter_opcs) >= 1:
                filtered_df.apply_farm_filter(options=farm_filter_opcs, refer_column='Name')
                filtered_status_loc.apply_farm_filter(options=farm_filter_opcs, refer_column='farm_name')
            filtered_df.apply_battery_filter(bat_min=min_bat, bat_max=max_bat)

    filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime')
    filtered_status_loc.apply_date_filter(start=inicio, end=fim, refer_column='Date')
    
    messages_per_day = filtered_df.df.groupby(by='PLM').count().reset_index()
    messages_per_day.rename(columns={'Identifier':'Sent Messages'}, inplace=True)

    # Agrupamentos por PLM
    agrupado = filtered_df.df.groupby(by='PLM')
    loc_status_agrupado = filtered_status_loc.df.groupby(by='PLM')
    relative_bov_qtd =  len(agrupado)
    bovine_chart = Bovine_plms.plot_scatter_plm(agrupado, date_period=[inicio, fim], qtd=relative_bov_qtd)
    loc_status_chart = location_status_chart.location_status_chart(loc_status_agrupado)

    agrupado_bateria = filtered_df.df.groupby(by='PLM').max()
    agrupado_bateria.reset_index(inplace=True)
    concatenado = filtered_df.df[(filtered_df.df['PLM'].isin(agrupado_bateria['PLM'])) & (filtered_df.df['payloaddatetime'].isin(agrupado_bateria['payloaddatetime']))]

    c_switch, order_switch_ascending, order_switch_descending, *_, relative_bov_metric = st.columns(6, gap='small')
    with c_switch:
        switch = st_toggle_switch(label='See uplink and last battery figures', label_after=True, active_color='#F98800', inactive_color='#D3D3D3', track_color='#5E00F8')
    with relative_bov_metric:
        relative_bov_qtd =  len(filtered_df.df.PLM.unique())
    if not switch:
        st.plotly_chart(bovine_chart, use_container_width=True)
        st.markdown('###')
        st.plotly_chart(loc_status_chart, use_container_width=True)
    else:
        with order_switch_ascending:
            switch_ascending = st_toggle_switch(label='Order data ascending', label_after=True, active_color='#F98800', inactive_color='#D3D3D3',
                                                track_color='#5E00F8')
        with order_switch_descending:
            switch_descending = st_toggle_switch(label='Order data descending', label_after=True, active_color='#F98800', inactive_color='#D3D3D3',
                                                 track_color='#5E00F8')
        if not switch_descending and switch_ascending:
            messages_per_day.sort_values(by='Sent Messages', ascending=True, inplace=True)
            concatenado.sort_values('battery', ascending=True, inplace=True)
        elif not switch_ascending and switch_descending:
            messages_per_day.sort_values(by='Sent Messages', ascending=False, inplace=True)
            concatenado.sort_values('battery', ascending=False, inplace=True)
        elif switch_ascending and switch_descending:
            st.warning('Ordered by PLM number. Use only one switch')
            messages_per_day.sort_values(by='PLM', ascending=True, inplace=True)
            concatenado.sort_values(by='PLM', ascending=True, inplace=True)
        else:
            messages_per_day.sort_values(by='PLM', ascending=True, inplace=True)
            concatenado.sort_values(by='PLM', ascending=True, inplace=True)

        min_messages = int(messages_per_day['Sent Messages'].min())
        max_messages = int(messages_per_day['Sent Messages'].max())
        
        min_messages, max_messages = c_switch.slider(label='Messages Range', value=[min_messages, max_messages], 
                            min_value=min_messages, max_value=max_messages)
        
        mensagens_filtrado = Filters(data_frame=messages_per_day)
        mensagens_filtrado.apply_message_filter(min_qtd=min_messages, max_qtd=max_messages)
        messages_chart = messages_a_day.messages_a_day(data=mensagens_filtrado.df, date_period=[inicio, fim])
        last_bat = last_battery_chart_fig.last_battery(data=concatenado)
        st.plotly_chart(messages_chart, use_container_width=True)
        st.plotly_chart(last_bat, use_container_width=True)

if __name__ == '__main__':
    st.set_page_config(layout='wide', page_title='Dashboards SpaceVis')
    st.markdown(streamlit_style, unsafe_allow_html=True) 
    initialize_session_state()
    conn = start_connection()
    if not conn is False:
        run_queries()
        menu1, menu2, menu3 = st.columns(3)
        with open('style.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        with menu2:
            name, authentication_status, username = login_authenticator.login(form_name='Login', location='main')
        if authentication_status:
            with st.spinner('Loading data...'):
                start_app(user=username)
        elif authentication_status is None:
            with menu2:
                st_lottie(welcome, loop=True, quality='medium', width=700, height=350, speed=1)
                pass
        else:
            with menu2:
                st.error('Be sure your credentials are correct')