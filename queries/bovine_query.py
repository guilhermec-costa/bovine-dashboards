QUERY_BOVINE_DASHBOARD = """
SELECT * FROM public."bovinedashboards";
"""

COLUMNS_TO_DATAFRAME = """
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'bovinedashboards';
"""

BOVINE_NUMBER = """
SELECT count(*) FROM public."Eartags"
"""

BATTERY_MEAN_LAST_30DAYS = """
SELECT round(avg(battery)::numeric, 2) FROM public."bovinedashboards" bov
WHERE payloaddatetime BETWEEN (current_date - interval '1' month) AND current_date
"""

BATTERY_MEAN_LAST_60DAYS = """
SELECT round(avg(battery)::numeric, 2) FROM public."bovinedashboards" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' month) AND (current_date - interval '1' month)
"""

BATTERY_MEAN_LAST_24HOURS = """
SELECT round(avg(battery::numeric), 2) FROM public."bovinedashboards" bov
WHERE payloaddatetime BETWEEN (current_date - interval '1' day) AND current_date
"""

BATTERY_MEAN_LAST_48HOURS = """
SELECT round(avg(battery::numeric), 2) FROM public."bovinedashboards" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' day) AND (current_date - interval '1' day)
"""

BOVINE_PER_FARM = """
SELECT "Name", count(DISTINCT "PLM") FROM public."bovinedashboards"
GROUP BY "Name";
"""

BOVINE_PER_RACE = """
SELECT race_name Race, count(DISTINCT "PLM") Qtd FROM public."bovinedashboards"
GROUP BY race_name;
"""

BATTERY_METRICS_30DAYS = """
SELECT DISTINCT payloaddatetime::date, round(avg("battery"::numeric), 2), round(max("battery"::numeric),2), round(min("battery"::numeric),2)
FROM public."bovinedashboards"
WHERE payloaddatetime BETWEEN (current_date - interval '1' month) AND current_date
GROUP BY payloaddatetime::date
ORDER BY payloaddatetime::date
"""

MESSAGES_A_DAY = """
SELECT "PLM", count("PLM") messages FROM public."bovinedashboards"
GROUP BY "PLM"; 
"""