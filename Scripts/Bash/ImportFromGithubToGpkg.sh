#!/bin/bash

set -e

source "$(dirname "${BASH_SOURCE[0]}")/Environment.sh"

echo "Converting data from Github to GPKG..."

ogr2ogr -f "GPKG" -lco FID=fid -overwrite -nln Segments \
    "${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Segments.gpkg" \
    "${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Segments.geojson"
echo "✓ Segments converted successfully."

ogr2ogr -f "GPKG" -lco FID=fid -overwrite -nln Compositions \
    "${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Compositions.gpkg" \
    "${ROUTES_DIR}/${COUNTRY_NAME}/${COUNTRY_NAME}_Compositions.geojson"
echo "✓ Compositions converted successfully."

echo "Data conversion completed."
