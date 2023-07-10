from . import bovine_query as bovn_q


queries_constants = [
    (bovn_q.QUERY_BOVINE_DASHBOARD, 'QUERY_BOVINE_DASHBOARD'), (bovn_q.COLUMNS_TO_DATAFRAME, 'COLUMNS_TO_DATAFRAME'), (bovn_q.BOVINE_NUMBER, 'BOVINE_NUMBER'),
    (bovn_q.BATTERY_MEAN_LAST_30DAYS, 'BATTERY_MEAN_LAST_30DAYS'), (bovn_q.BATTERY_MEAN_LAST_24HOURS, 'BATTERY_MEAN_LAST_24HOURS'), (bovn_q.BATTERY_MEAN_LAST_48HOURS, 'BATTERY_MEAN_LAST_48HOURS'),
    (bovn_q.BOVINE_PER_FARM, 'BOVINE_PER_FARM'), (bovn_q.BOVINE_PER_RACE, 'BOVINE_PER_RACE'), (bovn_q.LAST_BATTERY_QUERY, 'LAST_BATTERY_QUERY'), 
    (bovn_q.BATTERY_METRICS_30DAYS, 'BATTERY_METRICS_30DAYS'), (bovn_q.BATTERY_CATEGORIES, 'BATTERY_CATEGORIES'), (bovn_q.LOCATION_STATUS, 'LOCATION_STATUS'),
    (bovn_q.LAST_LOCATION, 'LAST_LOCATION')
]