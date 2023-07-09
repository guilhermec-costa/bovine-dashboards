QUERY_BOVINE_DASHBOARD = """
SELECT bd.*, b."Weight" FROM public."bovinedashboards2v" bd
JOIN "Bovines" b
	ON b."Id" = bd."BovineId"
"""

COLUMNS_TO_DATAFRAME = """
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'bovinedashboards2v';
"""

LAST_LOCATION = """
SELECT et."Identifier", et."PLM", r."Name", st_x(bovH."Location") latitude, st_y(bovH."Location") longitude, f."Name", 
bovH."CreatedAt", last_battery."battery"
FROM public."Eartags" et
LEFT JOIN "BovineHistories" bovH
	ON et."BovineId" = bovH."BovineId"
LEFT JOIN "Farms" f
	ON f."Id" = et."FarmId"
LEFT JOIN "Bovines" bov
	ON bov."Id" = et."BovineId"
LEFT JOIN "Races" r
	ON bov."RaceId" = r."Id"
LEFT JOIN
		(SELECT bv_dash1."PLM", bv_dash1.payloaddatetime, round(bv_dash2.battery::numeric, 3) battery
	FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash1
	JOIN (
		SELECT bv_dash2."PLM", bv_dash2.payloaddatetime, bv_dash2.battery
		FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash2
	) bv_dash2 ON bv_dash1."PLM" = bv_dash2."PLM" AND bv_dash1.payloaddatetime = bv_dash2.payloaddatetime
	WHERE bv_dash1.payloaddatetime = (
		SELECT max(payloaddatetime)
		FROM "eartag-ioda-prod".public.bovinedashboards2v
		WHERE "PLM" = bv_dash1."PLM"
	)
	ORDER BY bv_dash1.payloaddatetime DESC) last_battery
		ON last_battery."PLM" = et."PLM"
ORDER BY bovH."CreatedAt" DESC;
"""

BOVINE_NUMBER = """
SELECT count(*) FROM public."Eartags"
"""

BATTERY_MEAN_LAST_30DAYS = """
SELECT round(avg(battery)::numeric, 3) FROM public."bovinedashboards2v" bov
WHERE payloaddatetime BETWEEN (current_date - interval '30' day) AND current_date + interval '1' day;
"""

BATTERY_MEAN_LAST_60DAYS = """
SELECT round(avg(battery)::numeric, 2) FROM public."bovinedashboards2v" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' month) AND (current_date - interval '1' month)
"""

BATTERY_MEAN_LAST_24HOURS = """
SELECT round(avg(battery::numeric), 3) FROM public."bovinedashboards2v" bov
WHERE payloaddatetime BETWEEN (current_date - interval '1' day) AND current_date + interval '1' day;
"""

BATTERY_MEAN_LAST_48HOURS = """
SELECT round(avg(battery::numeric), 3) FROM public."bovinedashboards2v" bov
WHERE payloaddatetime BETWEEN (current_date - interval '2' day) AND (current_date - interval '1' day)
"""

BOVINE_PER_FARM = """
SELECT "Name", count(DISTINCT "PLM") FROM public."bovinedashboards2v"
GROUP BY "Name";
"""

BOVINE_PER_RACE = """
SELECT race_name Race, count(DISTINCT "PLM") Qtd FROM public."bovinedashboards2v"
GROUP BY race_name;
"""

BATTERY_METRICS_30DAYS = """
SELECT DISTINCT payloaddatetime::date, round(avg("battery"::numeric), 2), round(max("battery"::numeric),2), round(min("battery"::numeric),2)
FROM public."bovinedashboards2v"
WHERE payloaddatetime BETWEEN (current_date - interval '1' month) AND current_date
GROUP BY payloaddatetime::date
ORDER BY payloaddatetime::date
"""

MESSAGES_A_DAY = """
SELECT "PLM", count("PLM") messages FROM public."bovinedashboards2v"
GROUP BY "PLM"; 
"""

LAST_BATTERY_QUERY = """
SELECT bv_dash1."PLM", bv_dash1.payloaddatetime, round(bv_dash2.battery::numeric, 2)
FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash1
JOIN (
	SELECT bv_dash2."PLM", bv_dash2.payloaddatetime, bv_dash2.battery
	FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash2
) bv_dash2 ON bv_dash1."PLM" = bv_dash2."PLM" AND bv_dash1.payloaddatetime = bv_dash2.payloaddatetime
WHERE bv_dash1.payloaddatetime = (
	SELECT max(payloaddatetime)
	FROM "eartag-ioda-prod".public.bovinedashboards2v
	WHERE "PLM" = bv_dash1."PLM"
)
ORDER BY bv_dash1.payloaddatetime DESC;
"""

BATTERY_CATEGORIES = """
SELECT battery_indice, count(battery_indice) FROM (
SELECT bv_dash1."PLM", bv_dash1.payloaddatetime, round(bv_dash2.battery::numeric, 2) last_battery,
CASE
	WHEN bv_dash2.battery < 3.6 THEN 'Less than 3.6V'
	WHEN bv_dash2.battery <= 3.8 THEN 'Between 3.6V and 3.8V'
	ELSE 'Greater than 3.8V'
END battery_indice
FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash1
JOIN (
	SELECT bv_dash2."PLM", bv_dash2.payloaddatetime, bv_dash2.battery
	FROM "eartag-ioda-prod".public.bovinedashboards2v bv_dash2
) bv_dash2 ON bv_dash1."PLM" = bv_dash2."PLM" AND bv_dash1.payloaddatetime = bv_dash2.payloaddatetime
WHERE bv_dash1.payloaddatetime = (
	SELECT max(payloaddatetime)
	FROM "eartag-ioda-prod".public.bovinedashboards2v
	WHERE "PLM" = bv_dash1."PLM"
)
ORDER BY bv_dash1.payloaddatetime DESC) geral
GROUP BY battery_indice;
"""

LOCATION_STATUS = """
SELECT ea."PLM", ea."Identifier", "LocationStatus", "Date", r."Name", f."Name"  FROM public."BovineHistories" bh
LEFT JOIN "Eartags" ea ON
	bh."BovineId" = ea."BovineId"
JOIN "Farms" f ON
	ea."FarmId" = f."Id"
JOIN "Bovines" b ON
	ea."BovineId" = b."Id"
JOIN "Races" r ON
	b."RaceId" = r."Id"
"""