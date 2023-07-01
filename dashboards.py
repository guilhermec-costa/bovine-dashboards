import pandas as pd
import numpy as np
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
import datetime
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
limit_24h = datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - datetime.timedelta(days=1)
limit_48h = datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - datetime.timedelta(days=2)
limit_5days = datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - datetime.timedelta(days=5)

@st.cache_resource
def start_connection():
    try:
        return pgsql.connect(**st.secrets['postgres'])
    except Exception:
        st.error('Failed to connect to database.')
        return None

# Iniciando query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

recent_metrics = []
def run_queries():
    global content, bovine_per_farm, bovine_per_race, battery_mean_last48hours, battery_metrics_30days, recent_metrics, \
    columns_name, bovine_registers, battery_mean_last24hours, battery_mean_last_month, last_battery_data, volts_categories, location_status_data
    content = run_query(bovn_q.QUERY_BOVINE_DASHBOARD)
    columns_name = run_query(bovn_q.COLUMNS_TO_DATAFRAME)
    bovine_registers = run_query(bovn_q.BOVINE_NUMBER)[0][0]
    battery_mean_last_month = float(run_query(bovn_q.BATTERY_MEAN_LAST_30DAYS)[0][0])
    battery_mean_last24hours = run_query(bovn_q.BATTERY_MEAN_LAST_24HOURS)[0][0]
    battery_mean_last48hours = run_query(bovn_q.BATTERY_MEAN_LAST_48HOURS)[0][0]
    recent_metrics.append([battery_mean_last24hours, battery_mean_last48hours])
    recent_metrics = list(map(lambda x: float(x) if x is not None else 'No information', recent_metrics[0]))
    bovine_per_farm = pd.DataFrame(run_query(bovn_q.BOVINE_PER_FARM), columns=['Farm_name', 'Qtd'])
    bovine_per_race = pd.DataFrame(run_query(bovn_q.BOVINE_PER_RACE), columns=['Race_name', 'Qtd'])
    last_battery_data = pd.DataFrame(run_query(bovn_q.LAST_BATTERY_QUERY), columns=['PLM', 'payloaddatetime', 'battery'])
    battery_metrics_30days = pd.DataFrame(run_query(bovn_q.BATTERY_METRICS_30DAYS), columns=['Date', 'Mean', 'Max', 'Min'])
    if None not in (battery_mean_last24hours, battery_mean_last48hours):
        diff_last_day = round(battery_mean_last24hours - battery_mean_last48hours, 2)
    volts_categories = pd.DataFrame(run_query(bovn_q.BATTERY_CATEGORIES), columns=['Category', 'Quantity'])
    location_status_data = pd.DataFrame(run_query(bovn_q.LOCATION_STATUS), columns=['PLM', 'Status', 'Date', 'race_Name', 'farm_name'])

def initialize_session_state():
    # Inicializando as chaves necessárias no st.session_state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = False
    if 'status_opcs' not in st.session_state:
            st.session_state.status_opcs = ['Valid location', 'Invalid location']
    if 'logout' not in st.session_state:
        st.session_state.logout = False
    if 'apply_filters_button' not in st.session_state:
        st.session_state.apply_filters_button = False

def start_app(user):
    st.session_state.logout = False

    with st.sidebar:
        st.markdown('---')
        st.title(f'Your welcome {user.capitalize()}!')
        with st.spinner('Logging off...'):
            logout = login_authenticator.logout('Logout', 'main')
            st.session_state.logout = True if logout else False
    
    # Gráficos dos expanders
    farm_chart = pie_chart_farm.farm_chart(data=bovine_per_farm)
    race_chart = pie_chart_race.race_chart(data=bovine_per_race)
    volt_ranges = battery_categories.battery_categories(data=volts_categories)
    battery_chart = battery_30days.line_battery_chart(data=battery_metrics_30days)

    # Tratamento de dados
    location_status_data['Date'] = location_status_data['Date'].apply(lambda x: x if str(x) != '0001-01-01 00:00:00+00:00' else datetime.datetime.now(tz=pytz.timezone('Brazil/East')))
    location_status_data['Date'] = pd.to_datetime(location_status_data['Date'], utc=True, errors='coerce')
    location_status_data['Status'] = location_status_data['Status'].apply(lambda x: 'Valid location' if x else 'Invalid location')
    location_status_data['Mes-Dia'] = location_status_data['Date'].apply(lambda x: x.strftime('%b %d, %Y'))
    colunas = [x[0] for x in columns_name]
    colunas.append('Weight')
    df = pd.DataFrame(content, columns=colunas)
    df['payloaddatetime'] = pd.to_datetime(df['payloaddatetime'], utc=True)
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
    total_weight = np.sum(df.groupby(by='PLM').agg({'Weight': np.mean})['Weight'])
    # Exibindo as métricas
    metric1, metric2, metric3, *_ = st.columns(4, gap='medium')
    metric1.metric(label='Active bovines', value=bovine_registers, delta=f'{total_weight} Kg')
    metric2.metric(label='last 24 hours battery perfomance', value=f'{recent_metrics[0]}',
                    help='last 24 hours battery performance in comparison with the 48 last hours battery perfomance')
    metric3.metric(label='Medium battery on last 30 days', value=f'{battery_mean_last_month}V')
    
    style_metric_cards(background_color='#6D23FF', border_size_px=1.5, box_shadow=True, 
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
    download_btn.download_button(label='Download data', data=df.to_csv(), file_name=f'bovine_data_{datetime.datetime.now()}',
                                            mime='text/csv', key='download_btn', use_container_width=True)
    
    # Estilização da tabela principal
    vw_tab_aggrid = GridBuilder(df, key='filtered_df.df')
    tab_formatada, bovine_data = vw_tab_aggrid.grid_builder()
    clear_rows(bovine_data, drop_mode='any', drop_axis=0, sort_by_cols=['payloaddatetime', 'PLM'], sort_sequence=[False, True])

    filtered_df = Filters(data_frame=bovine_data)
    filtered_status_loc = Filters(data_frame=location_status_data)

    filtered_status_loc.df['Date'] = pd.to_datetime(filtered_status_loc.df.Date, errors='ignore')
    filtered_status_loc.df['Time'] = filtered_status_loc.df['Date'].apply(lambda x: x.time())
    filtered_df.df['payloaddatetime'] = pd.to_datetime(filtered_df.df.payloaddatetime)
    filtered_df.df['Time'] = filtered_df.df['payloaddatetime'].apply(lambda x: x.time())
    filtered_df.df['CreatedAt'] = pd.to_datetime(filtered_df.df.CreatedAt)

    c1_date, c2_date, c3_date, c4_date = st.columns(4)
    inicio = c1_date.date_input(label='Start date:', min_value=filtered_df.df['payloaddatetime'].min(), max_value=datetime.datetime.today(),
                        key='data_inicio', value=datetime.datetime.now() - datetime.timedelta(days=2))
    fim = c2_date.date_input(label='End date:', min_value=filtered_df.df['CreatedAt'].min(),
                    key='data_fim', value=datetime.datetime.now() + datetime.timedelta(days=1))
    hora_inicio = c3_date.time_input(label='Start time:', value=datetime.time(0,0))
    hora_final = c4_date.time_input(label='End time', value=datetime.time(23, 59))

    inicio = datetime.datetime.combine(inicio, datetime.datetime.min.time(), tzinfo=pytz.UTC)
    fim = datetime.datetime.combine(fim, datetime.datetime.min.time(), tzinfo=pytz.UTC)
    c1_farm, c2_plm, c3_race = st.columns(3)

    farm_filter_opcs = c1_farm.multiselect(label='Choose a farm', options=filtered_df.df['Name'].unique(), key='farm_filter')
    if len(farm_filter_opcs) >= 1:
        filtered_df.apply_farm_filter(options=farm_filter_opcs, refer_column='Name')
        filtered_status_loc.apply_farm_filter(options=farm_filter_opcs, refer_column='farm_name')
    
    race_filter_options = c3_race.multiselect(label='Choose a race', options=filtered_df.df['race_name'].unique(), key='race_filter')
    if len(race_filter_options) >= 1:
        filtered_df.apply_race_filter(options=race_filter_options, refer_column='race_name')
        filtered_status_loc.apply_race_filter(options=race_filter_options, refer_column='race_Name')
    
    plm_filter_options = c2_plm.multiselect(label='Choose any PLM', options=filtered_df.df['PLM'].unique(), key='plm_filter')
    if len(plm_filter_options) >= 1: 
        filtered_df.apply_plm_filter(options=plm_filter_options, refer_column='PLM')
        filtered_status_loc.apply_plm_filter(options=plm_filter_options, refer_column='PLM')

    bat_slider, weight_slider = st.columns(2, gap='large')
    relative_min_battery = float(filtered_df.df['battery'].min())
    relative_max_battery = float(filtered_df.df['battery'].max())
    relative_min_weight = float(filtered_df.df['Weight'].min())
    relative_max_weight = float(filtered_df.df['Weight'].max())
    min_bat, max_bat = bat_slider.slider(label='Battery range', value=[relative_min_battery, relative_max_battery], 
            min_value=relative_min_battery,max_value=relative_max_battery, step=0.05, help='Only can be applied to the battery level per bovine figure.')

    if relative_min_weight < relative_max_weight:
        min_weight, max_weight = weight_slider.slider(label='Weight range', value=[relative_min_weight, relative_max_weight],
                                                  min_value=relative_min_weight,max_value=relative_max_weight, step=25.0, help='Only can be applied to the battery level per bovine figure.')
        filtered_df.apply_weight_filter(min_weight=min_weight, max_weight=max_weight)
    else:
        weight_slider.warning('MIN WEIGHT equal/greater than MAX WEIGHT')
    
    filtered_df.apply_battery_filter(bat_min=min_bat, bat_max=max_bat)
    filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime', trigger_error=True)
    filtered_status_loc.apply_date_filter(start=inicio, end=fim, refer_column='Date')

    filtered_df.apply_time_filter(start_time=hora_inicio, end_time=hora_final, trigger_error=True)
    filtered_status_loc.apply_time_filter(start_time=hora_inicio, end_time=hora_final)

    messages_per_day = filtered_df.df.groupby(by='PLM').count().reset_index()
    messages_per_day.rename(columns={'Identifier':'Sent Messages'}, inplace=True)
    min_messages = int(messages_per_day['Sent Messages'].min())
    max_messages = int(messages_per_day['Sent Messages'].max())
    
    # Gráfico principal
    agrupado = filtered_df.df.groupby(by='PLM')
    relative_bov_qtd =  len(agrupado)
    bovine_chart = Bovine_plms.plot_scatter_plm(agrupado, date_period=[inicio, fim], qtd=relative_bov_qtd)

    agrupado_bateria = filtered_df.df.groupby(by='PLM').max()
    agrupado_bateria.reset_index(inplace=True)
    concatenado = filtered_df.df[(filtered_df.df['PLM'].isin(agrupado_bateria['PLM'])) & (filtered_df.df['payloaddatetime'].isin(agrupado_bateria['payloaddatetime']))]

    c_switch, order_switch_ascending, order_switch_descending, *_, relative_bov_metric = st.columns(6, gap='small')
    relative_bov_qtd =  len(filtered_df.df.PLM.unique())

    # Configuração dos switchs
    with c_switch:
        switch = st_toggle_switch(label='See uplink and last battery figures', label_after=True, active_color='#F98800', inactive_color='#D3D3D3', track_color='#5E00F8')
    if not switch:
        st.plotly_chart(bovine_chart, use_container_width=True)
        st.markdown('---')
        switch_location_count = st_toggle_switch(label='See more details', label_after=True, active_color='#F98800', inactive_color='#D3D3D3', track_color='#5E00F8')
        barmode = 'group'
        if not switch_location_count:
            with st.expander('Edit figure'):
                with st.form(key='chart_filters_count'):
                    chart_mode, *_ = st.columns(6)
                    with chart_mode:
                        chart_mode_switch = st.radio(label='Choose a chart mode', options=['Only Bars', 'Only Lines', 'Mix'], horizontal=True)
                        status_opcs = st.multiselect('Status filters', options=['Valid location', 'Invalid location'])
                    if chart_mode_switch == 'Only Bars':
                        barmode_widget, *_ = st.columns(6)
                        barmode = barmode_widget.selectbox('Choose a barmode:', options=['Group', 'Stack'], index=0)

                    if st.form_submit_button('Apply filters'):
                        if len(status_opcs) >= 1:
                            filtered_status_loc.apply_status_filter(options=status_opcs)
                            st.session_state.status_opcs = status_opcs
            status_loc_agrupado = filtered_status_loc.df.groupby(by=['Mes-Dia', 'Status']).count()['PLM']
            status_loc_agrupado.index = pd.MultiIndex.from_tuples(
            [(pd.to_datetime(date, format="%b %d, %Y"), status) for date, status in status_loc_agrupado.index])
            status_loc_unstacked = status_loc_agrupado.sort_index(level=0).unstack(level=1)
            loc_status_count_chart = location_status_chart.count_location_status(status_loc_unstacked,
                                                                                  mode=chart_mode_switch, barmode=barmode.lower(),
                                                                                  columns_to_add = status_loc_unstacked.columns)
            st.plotly_chart(loc_status_count_chart, use_container_width=True)
        else:
            filtered_status_loc.apply_status_filter(options=st.session_state.status_opcs)
            loc_status_agrupado = filtered_status_loc.df.groupby(by='PLM')
            loc_status_chart = location_status_chart.location_status_chart(loc_status_agrupado)
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
        elif (switch_ascending and switch_descending) or (not switch_ascending and not switch_descending):
            st.warning('Ordered by PLM number.')
            messages_per_day.sort_values(by='PLM', ascending=True, inplace=True)
            concatenado.sort_values(by='PLM', ascending=True, inplace=True)

        if len(messages_per_day) > 1:
            min_messages, max_messages = c_switch.slider(label='Messages Range', value=[min_messages, max_messages], 
                                                        min_value=min_messages, max_value=max_messages)
        
        mensagens_filtrado = Filters(data_frame=messages_per_day)
        mensagens_filtrado.apply_message_filter(min_qtd=min_messages, max_qtd=max_messages)
        messages_chart = messages_a_day.messages_a_day(data=mensagens_filtrado.df, date_period=[inicio, fim])
        last_bat = last_battery_chart_fig.last_battery(data=concatenado)
        st.plotly_chart(messages_chart, use_container_width=True)
        st.plotly_chart(last_bat, use_container_width=True)

if __name__ == '__main__':
    st.set_page_config(layout='wide', page_title='Dashboards SpaceVis', initial_sidebar_state='collapsed', page_icon=':bar_chart:')
    st.markdown(streamlit_style, unsafe_allow_html=True) 
    initialize_session_state()
    conn = start_connection()
    if not conn is None:
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
                st_lottie(welcome, loop=True, quality='medium', width=700, height=350, speed=1)