QUERY_BOVINE_DASHBOARD = """
    SELECT * FROM public."bovinedashboard";
"""

COLUMNS_TO_DATAFRAME = """
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'bovinedashboard';
"""