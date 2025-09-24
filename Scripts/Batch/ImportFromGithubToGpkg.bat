@echo off

echo This script imports "two geojson files in a github environment" to a "geopackage network in a qGis environment"

set WORKING_DIR=%~dp0
set WORKING_DIR=%WORKING_DIR:~0,-1%

call "%WORKING_DIR%"\Settings.bat
call "%WORKING_DIR%"\Environment.bat

if exist "%NETWORK%" del /F /Q "%NETWORK%"
ogr2ogr -f GPKG "%NETWORK%" %SEGMENTS% -a_srs EPSG:%EPSG% -nln Segments -sql "SELECT CAST(id AS INTEGER) AS id, * FROM Segments" -lco FID=id -overwrite --debug %DEBUG%
ogr2ogr -f GPKG "%NETWORK%" %COMPOSITIONS% -nln Compositions -nlt NONE -append --debug %DEBUG%

pause



