@echo off

echo This script exports a "geopackage network in a qGis environment" to "two geojson files in a github environment"

set WORKING_DIR=%~dp0
set WORKING_DIR=%WORKING_DIR:~0,-1%

call "%WORKING_DIR%"\Settings.bat
call "%WORKING_DIR%"\Environment.bat

if exist "%SEGMENTS%" del /F /Q "%SEGMENTS%"
ogr2ogr -f GeoJSON -overwrite "%SEGMENTS%" "%NETWORK%" -a_srs EPSG:%EPSG% -lco RFC7946=NO -lco COORDINATE_PRECISION=2 -sql "SELECT id AS id, * FROM Segments" --debug %DEBUG%

if exist "%COMPOSITIONS%" del /F /Q "%COMPOSITIONS%"
ogr2ogr -f GeoJSON -overwrite "%COMPOSITIONS%" "%NETWORK%" Compositions --debug %DEBUG%

pause



