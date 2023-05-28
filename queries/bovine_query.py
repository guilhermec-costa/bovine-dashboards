QUERY_BOVINE_DASHBOARD = """
    SELECT * FROM public."bovinedashboard";
"""

COLUMNS_TO_DATAFRAME = """
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'bovinedashboard';
"""

BOVINE_NUMBER = """
SELECT count(*) FROM public."Eartags"
"""

BATTERY_MEAN_LAST_30DAYS = """
SELECT round(avg(battery)::numeric, 2) FROM public."bovinedashboard" bov
WHERE payloaddatetime BETWEEN (current_date - interval '1' month) AND current_date
"""

BATTERY_MEAN_LAST_60DAYS = """
SELECT round(avg(battery)::numeric, 2) FROM public."bovinedashboard" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' month) AND (current_date - interval '1' month)
"""

BATTERY_MEAN_LAST_24HOURS = """
SELECT round(avg(battery::numeric), 2) FROM public."bovinedashboard" bov
WHERE payloaddatetime BETWEEN (current_date- interval '1' day) AND current_date
"""

BATTERY_MEAN_LAST_48HOURS = """
SELECT round(avg(battery::numeric), 2) FROM public."bovinedashboard" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' day) AND (current_date - interval '1' day)
"""