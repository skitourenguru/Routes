************************************************************************
************************** Update data in Database **********************
************************************************************************
	
-- Truncate the existing tables

TRUNCATE TABLE compositions, segments;

-- Disable the triggers

ALTER TABLE compositions
DISABLE TRIGGER ALL;

ALTER TABLE segments
DISABLE TRIGGER ALL;

------------------------------------------------------------------------------------
Adapt and copy this line in your shell :
ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=test" /home/ulysse/Dropbox/skitourenguru/Ski-Routes/France-Alpes/France_Alpes_Compositions.geojson && ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=test" /home/ulysse/Dropbox/skitourenguru/Ski-Routes/France-Alpes/France_Alpes_Segments.geojson	
---------------------------------------------------------------------------------

	
-- Enable again the triggers
	
ALTER TABLE compositions
ENABLE TRIGGER ALL;

ALTER TABLE segments
ENABLE TRIGGER ALL;

-- Insert a first time geometry into compositions layer.

WITH
    a AS (SELECT compositions.id, st_collect(segments.geom) AS geom
		FROM compositions, UNNEST(segments) AS iti 
		JOIN segments ON segments.id = iti 
		GROUP BY compositions.id)

	UPDATE compositions
	SET geom = a.geom
	FROM a
	WHERE a.id = compositions.id;
