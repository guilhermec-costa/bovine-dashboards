import pandas as pd
import numpy as np
import streamlit as st
import psycopg2 as pgsql
from grid_builder import GridBuilder
from filters import Filters
from figures import (Bovine_plms, last_location_map, pie_chart_farm, pie_chart_race, battery_30days, location_status_chart,
                    messages_a_day, last_battery_chart_fig, battery_categories, pie_chart_messages, location_status_count_chart,
                    boxplot_battery)
from data_treatement.data_dealer import *
from streamlit_extras.metric_cards import style_metric_cards
from authenticator import login_authenticator
from streamlit_extras.toggle_switch import st_toggle_switch
import lottie_loader
import datetime
import pytz
from streamlit_lottie import st_lottie
import constructors
from queries.queries_runner import Queries
from queries.queries_constants import queries_constants
from zipfile import ZipFile
from pathlib import Path
from downloads_handler import manage_downloads

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
    if 'download_zip' not in st.session_state:
        st.session_state.download_zip = False


def start_app(user, queries_results):
    recent_metrics = []
    colunas = [x[0] for x in queries_results.get('COLUMNS_TO_DATAFRAME')]
    colunas.append('Weight')
    df = pd.DataFrame(queries_results.get('QUERY_BOVINE_DASHBOARD'), columns=colunas)
    bovine_per_farm = pd.DataFrame(queries_results.get('BOVINE_PER_FARM'), columns=['Farm_name', 'Qtd'])
    bovine_per_race = pd.DataFrame(queries_results.get('BOVINE_PER_RACE'), columns=['Race_name', 'Qtd'])
    volts_categories = pd.DataFrame(queries_results.get('BATTERY_CATEGORIES'), columns=['Category', 'Quantity'])
    location_status_data = pd.DataFrame(queries_results.get('LOCATION_STATUS'), columns=['PLM', 'Deveui', 'Status', 'Date', 'race_name', 'Name'])
    battery_metrics_30days = pd.DataFrame(queries_results.get('BATTERY_METRICS_30DAYS'), columns=['Date', 'Mean', 'Max', 'Min'])
    bovine_registers = queries_results.get('BOVINE_NUMBER')[0][0]
    battery_mean_last_month = float(queries_results.get('BATTERY_MEAN_LAST_30DAYS')[0][0])
    battery_mean_last24hours = float(queries_results.get('BATTERY_MEAN_LAST_24HOURS')[0][0])
    battery_mean_last48hours = float(queries_results.get('BATTERY_MEAN_LAST_48HOURS')[0][0])
    recent_metrics.append([battery_mean_last24hours, battery_mean_last48hours])
    recent_metrics = list(map(lambda x: f'{float(x)}V' if x is not None else 'No information', recent_metrics[0]))
    if 'No information' not in (recent_metrics): diff_last_day = round(battery_mean_last24hours - battery_mean_last48hours, 4)
    else: diff_last_day = None
    last_location = pd.DataFrame(queries_results.get('LAST_LOCATION'), columns=['Deveui', 'PLM', 'race_name', 'Longitude', 'Latitude', 'Name', 'Date', 'battery'])
    last_location.dropna(axis=0, subset=['Date'], inplace=True)
    last_location.sort_values(by='Date', ascending=False, inplace=True)
    last_location['battery'] = last_location['battery'].astype(float)

    st.markdown("###")
    with st.sidebar:
        st.title('Spacevis Dashboards :bar_chart:')
        st.markdown('---')
        st.markdown(f'<h2>Your welcome <strong style="color: #FF9430; text-weight:bold;">{user.capitalize()}</strong>!</h2>', unsafe_allow_html=True)
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
    df['payloaddatetime'] = pd.to_datetime(df['payloaddatetime'], utc=True)
    df['battery'] = df['battery'].apply(lambda x: x / 1000 if x > 100 else x)
    df.rename(columns={'Identifier':'Deveui'}, inplace=True)

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
    act_bovines, weight, bat_24h, bat_30days = st.columns(4, gap='medium')
    act_bovines.metric(label='Active bovines', value=bovine_registers)
    
    weight.metric(label='Total bovine weight', value=f'{total_weight} Kg')
    bat_24h.metric(label='last 24 hours battery perfomance', value=f'{recent_metrics[0]}', delta=diff_last_day,
                    help='last 24 hours battery performance in comparison with the 48 last hours battery perfomance')
    bat_30days.metric(label='Medium battery on last 30 days', value=f'{battery_mean_last_month}V')
    
    style_metric_cards(background_color='#6D23FF', border_size_px=1.5, box_shadow=True, 
                    border_color='#39275B', border_radius_px=25, border_left_color='#39275B')
    st.markdown("###")

    battery_expander = constructors.ExpanderConstructor(2, 'plotly_chart', (volt_ranges, pie_chart_limits), 'Battery perfomance', container_size=True)
    general_metrics = constructors.ExpanderConstructor(2, 'plotly_chart', (farm_chart, race_chart), 'General Metrics', container_size=True)
    battery_expander.add_plot(1, (battery_chart))
    
    battery_expander.build_expander()
    general_metrics.build_expander()
    
    # Estilização da tabela principal
    # vw_tab_aggrid = GridBuilder(df, key='filtered_df.df')
    # tab_formatada, bovine_data = vw_tab_aggrid.grid_builder()
    clear_rows(df, drop_mode='any', drop_axis=0, sort_by_cols=['payloaddatetime', 'PLM'], sort_sequence=[False, True])
    clear_rows(last_location, drop_mode='any', drop_axis=0, sort_by_cols=['Date', 'PLM'], sort_sequence=[False, True])

    filtered_df = Filters(data_frame=df)
    filtered_status_loc = Filters(data_frame=location_status_data)
    filtered_last_location = Filters(data_frame=last_location)

    filtered_status_loc.df['Date'] = pd.to_datetime(filtered_status_loc.df.Date, errors='ignore')
    filtered_status_loc.df['Time'] = filtered_status_loc.df['Date'].apply(lambda x: x.time())
    filtered_last_location.df['Time'] = filtered_last_location.df['Date'].apply(lambda x: x.time())
    filtered_df.df['payloaddatetime'] = pd.to_datetime(filtered_df.df.payloaddatetime)
    filtered_df.df['Time'] = filtered_df.df['payloaddatetime'].apply(lambda x: x.time())
    filtered_df.df['CreatedAt'] = pd.to_datetime(filtered_df.df.CreatedAt)

    st.subheader('Filters')
    st.markdown('---')

    c1_date, c2_date = st.columns(2)
    inicio = c1_date.date_input(label='Start date:', min_value=filtered_df.df['payloaddatetime'].min(), max_value=datetime.datetime.today(),
                        key='data_inicio', value=datetime.datetime.now() - datetime.timedelta(days=1))
    fim = c2_date.date_input(label='End date:', min_value=filtered_df.df['CreatedAt'].min(),
                    key='data_fim', value=datetime.datetime.now())
    

    inicio = datetime.datetime.combine(inicio, datetime.datetime.min.time(), tzinfo=pytz.UTC)
    fim = datetime.datetime.combine(fim, datetime.datetime.min.time(), tzinfo=pytz.UTC)
    c1_farm, c2_race, c3_plm, c4_type_of_id = st.columns(4)

    farm_filter_opcs = c1_farm.multiselect(label='Choose a farm', options=filtered_df.df['Name'].unique(), key='farm_filter')
    filtered_df.validate_filter(filter_name='apply_farm_filter', opcs=farm_filter_opcs, refer_column='Name')
    filtered_status_loc.validate_filter(filter_name='apply_farm_filter', opcs=farm_filter_opcs, refer_column='Name')
    filtered_last_location.validate_filter(filter_name='apply_farm_filter', opcs=farm_filter_opcs, refer_column='Name')
    
    race_filter_options = c2_race.multiselect(label='Choose a race', options=filtered_df.df['race_name'].unique(), key='race_filter')
    filtered_df.validate_filter(filter_name='apply_race_filter', opcs=race_filter_options, refer_column='race_name')
    filtered_status_loc.validate_filter(filter_name='apply_race_filter', opcs=race_filter_options, refer_column='race_name')
    filtered_last_location.validate_filter(filter_name='apply_race_filter', opcs=race_filter_options, refer_column='race_name')
    
    identifier_options = c4_type_of_id.radio('Identifier to filter by', options=['PLM', 'Deveui'], horizontal=True)
    plm_filter_options = c3_plm.multiselect(label=f'Choose any {identifier_options}', options=filtered_df.df[identifier_options].unique(), key='plm_filter')
    filtered_df.validate_filter(filter_name=f'apply_{identifier_options}_filter'.lower(), opcs=plm_filter_options, refer_column=identifier_options)
    filtered_status_loc.validate_filter(filter_name=f'apply_{identifier_options}_filter'.lower(), opcs=plm_filter_options, refer_column=identifier_options)
    filtered_last_location.validate_filter(filter_name=f'apply_{identifier_options}_filter'.lower(), opcs=plm_filter_options, refer_column=identifier_options)

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
    
    filtered_df.apply_battery_filter(bat_min=min_bat, bat_max=max_bat, refer_column='battery')
    filtered_last_location.apply_battery_filter(bat_min=min_bat, bat_max=max_bat, refer_column='battery')
    filtered_df.apply_date_filter(start=inicio, end=fim, refer_column='payloaddatetime', trigger_error=True)
    filtered_status_loc.apply_date_filter(start=inicio, end=fim, refer_column='Date')
    filtered_last_location.apply_date_filter(start=inicio, end=fim, refer_column='Date')

    download_status = []
    with st.expander('Download filtered data'):
        main_data = st.checkbox('Include battery historic dataset', value=False, key='main_data')
        last_location_status_data = st.checkbox('Include last location status dataset', value=False, key='last_location_data')
        last_location_position_data = st.checkbox('Include last location dataset', value=False, key='last_location_position_data')
        gen_zip, download_zip, *_ = st.columns(10)
        generate_zip = gen_zip.button('Generate zipfile', key='zip_file', type='primary')
        download_status = manage_downloads(status_list=[('bovine_battery_historic', main_data, filtered_df), ('last_location_status', last_location_status_data, filtered_status_loc),
                                                        ('last_location_position_latlong', last_location_position_data, filtered_last_location)])
        if generate_zip:
            generated_time = datetime.datetime.now(tz=pytz.timezone('Brazil/East')).strftime(f'%Y-%b-%d_%Hh_%Mm_%Ss')
            zip_name = f'bovine_dash-{generated_time}.zip'

            with st.spinner('Generating zip file...'):
                with ZipFile(zip_name, 'w') as zip_file:
                    for download in download_status:
                        for key, value in download[0].items():
                            if value:
                                arquivo_csv = download[1].df.to_csv(f'{key}.csv', sep=';')
                                zip_object = zip_file.write(f'{key}.csv')
                                Path.unlink(f'{key}.csv')

            with open(zip_name, 'rb') as zip_file_readed:
                zip_to_download = zip_file_readed.read()
            download_zip = download_zip.download_button('Download zip file', data=zip_to_download, file_name=zip_name, mime='application/zip')
            Path.unlink(zip_name)


    messages_per_day = filtered_df.df.groupby(by='PLM').count().reset_index()
    messages_per_day.rename(columns={'Deveui':'Sent Messages'}, inplace=True)
    if messages_per_day.shape[0] >= 1:
        min_messages = int(messages_per_day['Sent Messages'].min())
        max_messages = int(messages_per_day['Sent Messages'].max())
    else:
        min_messages, max_messages = [0, 0]
    
    # Gráfico principal
    agrupado = filtered_df.df.groupby(by=identifier_options)
    boxplot_data = filtered_df.df[['PLM', 'battery', 'payloaddatetime']].copy()
    boxplot_data['payloaddatetime'] = boxplot_data['payloaddatetime'].dt.date
    last_location_grouped = filtered_last_location.df.groupby(by='PLM').max().reset_index()
    last_location_grouped = filtered_last_location.df.groupby(by='PLM').agg({'Date':'max'}).reset_index().merge(filtered_last_location.df, on=['PLM', 'Date'])
    relative_bov_qtd =  len(agrupado)
    bovine_chart = Bovine_plms.plot_scatter_plm(agrupado, date_period=[inicio, fim], qtd=relative_bov_qtd, id_kind=identifier_options)

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
        c_show_all_points, *_ = st.columns(5)
        show_all_points = c_show_all_points.radio(label='Include:', options=['only outliers', 'inliers + outliers'], horizontal=True,
                                                  key='boxplot_all_points', label_visibility='visible')
        enable_grouping = c_show_all_points.checkbox('Group by individual bovine', value=False, key='boxplot_group_bovine')
        
        if enable_grouping:
            boxplot_data = boxplot_data.groupby(by=['payloaddatetime', 'PLM']).agg({'battery':'mean'}).reset_index()
            
        fig_boxplot = boxplot_battery.boxplot_battery(boxplot_data, point_dist=show_all_points)
        st.plotly_chart(fig_boxplot, use_container_width=True)
        st.markdown('---')
        barmode = 'group'
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

        if len(messages_per_day) > 1 and min_messages != max_messages:
            min_messages, max_messages = c_switch.slider(label='Messages Range', value=[min_messages, max_messages], 
                                                        min_value=min_messages, max_value=max_messages)
        
        mensagens_filtrado = Filters(data_frame=messages_per_day)
        mensagens_filtrado.apply_message_filter(min_qtd=min_messages, max_qtd=max_messages)
        messages_chart = messages_a_day.messages_a_day(data=mensagens_filtrado.df, date_period=[inicio, fim])
        last_bat = last_battery_chart_fig.last_battery(data=concatenado)
        st.plotly_chart(messages_chart, use_container_width=True)
        st.plotly_chart(last_bat, use_container_width=True)

    st.markdown('###')
    st.title('Location analysis', anchor=None)
    st.markdown('---')
    col_status, *_ = st.columns(9)
    status_opcs = col_status.multiselect('Status filters', options=['Valid location', 'Invalid location'])
    if len(status_opcs) >= 1:
        filtered_status_loc.apply_status_filter(options=status_opcs)
        st.session_state.status_opcs = status_opcs

    status_loc_agrupado = filtered_status_loc.df.groupby(by=['Mes-Dia', 'Status']).count()['PLM']
    status_loc_agrupado.index = pd.MultiIndex.from_tuples(
    [(pd.to_datetime(date, format="%b %d, %Y"), status) for date, status in status_loc_agrupado.index])
    filtered_status_loc.df['Date'] = filtered_status_loc.df['Date'].dt.date.apply(lambda x: datetime.datetime.strftime(x, '%b %d, %Y'))
    status_loc_count_per_plm = filtered_status_loc.df.groupby(by=['PLM', 'Status', 'Date']).count()

    all_avalaible_status = set([tupla[1] for tupla in status_loc_count_per_plm.index])

    status_count_drilldown = st.radio('Do Drilldown', options=['Drill Up by location status', 'Drill Down by location status'], index=0, label_visibility='hidden')
    if status_count_drilldown.__contains__('Up'):
        switch_location_count = st_toggle_switch(label='See more details', label_after=True, active_color='#F98800', inactive_color='#D3D3D3', track_color='#5E00F8')
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
                        pass

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
    elif status_count_drilldown.__contains__('Down'):
        if 'Valid location' in all_avalaible_status:
            contagem_loc_valida = status_loc_count_per_plm['Name'].unstack(level='Status').reset_index()[['PLM', 'Date', 'Valid location']].dropna(axis=0, subset='Valid location')
            contagem_loc_valida_agrupado = contagem_loc_valida.groupby(by=['Date', 'Valid location']).count().reset_index()
            fig_validos = location_status_count_chart.valid_status_count(contagem_loc_valida_agrupado)
            st.plotly_chart(fig_validos, use_container_width=True)
        st.markdown('---')
        if 'Invalid location' in all_avalaible_status:
            contagem_loc_invalida = status_loc_count_per_plm['Name'].unstack(level='Status').reset_index()[['PLM', 'Date', 'Invalid location']].dropna(axis=0, subset='Invalid location')
            contagem_loc_invalida_agrupado = contagem_loc_invalida.groupby(by=['Date', 'Invalid location']).count().reset_index()
            fig_invalidos = location_status_count_chart.invalid_status_count(contagem_loc_invalida_agrupado)
            st.plotly_chart(fig_invalidos, use_container_width=True)
    
    st.markdown('---')
    theme_position, *_ = st.columns(5)
    theme_options = ['satellite', 'satellite-streets', 'carto-positron', 'carto-darkmatter', 'dark', 'open-street-map', 'streets', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
    choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
    last_location_chart = last_location_map.mapbox_last_location(last_location_grouped, theme=choosed_theme, ident = identifier_options)
    st.plotly_chart(last_location_chart, use_container_width=True)


if __name__ == '__main__':
    st.set_page_config(layout='wide', page_title='Dashboards SpaceVis', page_icon=':bar_chart:', initial_sidebar_state='expanded')
    st.markdown(streamlit_style, unsafe_allow_html=True) 
    initialize_session_state()
    queries = Queries()
    if not queries.connection is None:
        queries.add_queries(queries_constants)
        ALL_RESULTS = queries.run_queries()
        menu1, menu2, menu3 = st.columns(3)
        with open('style.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        with menu2:
            name, authentication_status, username = login_authenticator.login(form_name='Login', location='main')
        if authentication_status:
            with st.spinner('Loading data...'):
                start_app(user=username, queries_results=ALL_RESULTS)
        elif authentication_status is None:
            with menu2:
                st_lottie(welcome, loop=True, quality='medium', width=700, height=350, speed=1)
                pass
        else:
            with menu2:
                st.error('Be sure your credentials are correct')
                st_lottie(welcome, loop=True, quality='medium', width=700, height=350, speed=1)