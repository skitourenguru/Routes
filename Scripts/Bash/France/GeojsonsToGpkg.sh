#!/bin/bash

# Path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR/../../.."


# Path to the files
FRANCE_OTHER_SEGMENTS="$BASE_DIR/France-Other/France-Other_Segments.geojson"
FRANCE_OTHER_COMPOSITIONS="$BASE_DIR/France-Other/France-Other_Compositions.geojson"

FRANCE_ALPES_SEGMENTS="$BASE_DIR/France/France_Segments.geojson"
FRANCE_ALPES_COMPOSITIONS="$BASE_DIR/France/France_Compositions.geojson"

PYRENEES_SEGMENTS="$BASE_DIR/Pyrenees/Pyrenees_Segments.geojson"
PYRENEES_COMPOSITIONS="$BASE_DIR/Pyrenees/Pyrenees_Compositions.geojson"

# Output GPKG file
OUTPUT_SEGMENTS="$BASE_DIR/France_Complete_Segments.gpkg"
OUTPUT_COMPOSITIONS="$BASE_DIR/France_Complete_Compositions.gpkg"


# Merge the GeoJSON files into a single GPKG
ogrmerge.py \
  -f GPKG \
  -overwrite_ds \
  -o "$OUTPUT_SEGMENTS" \
  "$FRANCE_OTHER_SEGMENTS" \
  "$FRANCE_ALPES_SEGMENTS" \
  "$PYRENEES_SEGMENTS" \
  -single \
  -nln Segments

ogrmerge.py \
  -f GPKG \
  -overwrite_ds \
  -o "$OUTPUT_COMPOSITIONS" \
  "$FRANCE_OTHER_COMPOSITIONS" \
  "$FRANCE_ALPES_COMPOSITIONS" \
  "$PYRENEES_COMPOSITIONS" \
  -single \
  -nln Compositions
