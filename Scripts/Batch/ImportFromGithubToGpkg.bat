@echo off

echo This script imports "two geojson files in a github environment" to a "geopackage network in a qGis environment"

set WORKING_DIR=%~dp0
set WORKING_DIR=%WORKING_DIR:~0,-1%

call "%WORKING_DIR%"\Settings.bat
call "%WORKING_DIR%"\Environment.bat

if exist "%NETWORK%" (
	echo WARNING: 
	echo The target file %NETWORK% 
	echo in the qGis environment exists already. 
	echo If you press now any key, it will be overwritten and lost! 
    choice /c YN /m "Press Y(Yes) to overwrite or N(No) to cancel."

    if errorlevel 2 (
        echo Operation cancelled.
        exit /b
    )	
)

if exist "%INTERMEDIATE_SEGMENTS%" del /F /Q "%INTERMEDIATE_SEGMENTS%"
ogr2ogr -f GeoJSON %INTERMEDIATE_SEGMENTS% %SEGMENTS% -sql "SELECT id AS myown, length FROM Segments" -overwrite 

if exist "%NETWORK%" del /F /Q "%NETWORK%"
ogr2ogr -unsetFid -f GPKG "%NETWORK%" %INTERMEDIATE_SEGMENTS% -nln Segments -a_srs EPSG:%EPSG% -overwrite --debug %DEBUG%
ogr2ogr -f GPKG "%NETWORK%" %COMPOSITIONS% -nln Compositions -nlt NONE -append --debug %DEBUG%

ogrinfo -sql "alter table Segments add column id integer" "%NETWORK%"
ogrinfo -dialect sqlite -sql "update Segments set id=myown" "%NETWORK%"
ogrinfo -dialect sqlite -sql "ALTER TABLE Segments DROP COLUMN myown" "%NETWORK%"

pause



