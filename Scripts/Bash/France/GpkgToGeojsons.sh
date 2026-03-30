#!/bin/bash

# Path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR/../../.."

# GPKG files
SEGMENTS="$BASE_DIR/France_Complete_Segments.gpkg"
COMPOSITIONS="$BASE_DIR/France_Complete_Compositions.gpkg"

regions=("France" "France-Other" "Pyrenees")

FILTER_OTHER="massif IN ('Vosges', 'Jura', 'Massif Central', 'Corse')"
FILTER_FRANCE="massif NOT IN ('Vosges', 'Jura', 'Massif Central', 'Corse', 'Pyrénées')"
FILTER_PYRENEES="massif IN ('Pyrénées')"

for region in "${regions[@]}"; do
    case $region in
        "France")
            FILTER=$FILTER_FRANCE
            ;;
        "France-Other")
            FILTER=$FILTER_OTHER
            ;;
        "Pyrenees")
            FILTER=$FILTER_PYRENEES
            ;;
    esac

    OUTPUT_SEGMENTS="$BASE_DIR/$region/${region}_Segments.geojson"
    OUTPUT_COMPOSITIONS="$BASE_DIR/$region/${region}_Compositions.geojson"

    mkdir -p "$BASE_DIR/$region"
    rm -f "$OUTPUT_SEGMENTS" "$OUTPUT_COMPOSITIONS"

    ogr2ogr \
        -f "GeoJSON" \
        -overwrite \
        -lco COORDINATE_PRECISION=2 \
        -nln  "Segments" \
        -sql  "SELECT * FROM Segments WHERE $FILTER  AND importance = 0 ORDER BY id" \
        "$OUTPUT_SEGMENTS" \
        "$SEGMENTS"

    ogr2ogr \
        -f "GeoJSON" \
        -overwrite \
        -lco COORDINATE_PRECISION=2 \
        -nlt NONE \
        -nln  "Compositions" \
        -sql  "SELECT * FROM Compositions WHERE $FILTER AND importance = 0 ORDER BY id" \
        "$OUTPUT_COMPOSITIONS" \
        "$COMPOSITIONS"
done
