#!/bin/bash

set -e

source "$(dirname "${BASH_SOURCE[0]}")/Environment.sh"

echo "Converting data from GPKG to GeoJSON..."

SEGMENTS="${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Segments"

rm -f "${SEGMENTS}.geojson"
ogr2ogr -f "GeoJSON" -overwrite -lco COORDINATE_PRECISION=2 -nln Segments \
    -sql "SELECT id, geom FROM Segments ORDER BY id" \
    "${SEGMENTS}.geojson" \
    "${SEGMENTS}.gpkg"
echo "✓ Segments converted successfully."

COMPOSITIONS="${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Compositions"

rm -f "${COMPOSITIONS}.geojson"
ogr2ogr -f "GeoJSON" -overwrite -nln Compositions \
    -sql "SELECT NULL AS geom, * FROM Compositions ORDER BY id" \
    "${COMPOSITIONS}.geojson" \
    "${COMPOSITIONS}.gpkg"
echo "✓ Compositions converted successfully."

echo "All data converted successfully."
