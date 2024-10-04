#!/bin/bash

# Permet de renouveller à partir des sauvegardes les données de Segments et Compositions dans la base de données.

# Modifiez seulement les deux variables ci-dessous :

db="test"
dossier="/home/ulysse/Dropbox/skitourenguru/Routes/France/"


psql -U postgres -d $db <<EOF
-- Truncate the existing tables
TRUNCATE TABLE compositions, segments;

-- Disable the triggers
ALTER TABLE compositions DISABLE TRIGGER ALL;
ALTER TABLE segments DISABLE TRIGGER ALL;

-- Change data type
ALTER TABLE compositions ALTER COLUMN segments TYPE TEXT USING array_to_string(segments, ',');
EOF

# Import GeoJSON data
ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=$db" $dossier/France_Compositions.geojson
ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=$db" $dossier/France_Segments.geojson

psql -U postgres -d $db <<EOF
-- Enable the triggers again
ALTER TABLE compositions ENABLE TRIGGER ALL;
ALTER TABLE segments ENABLE TRIGGER ALL;

-- Change data type again
ALTER TABLE compositions ALTER COLUMN segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[];

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

EOF
