
rem GDAL as standalone installation
rem -------------------------------------------------------------------

rem Here change gdal directory
rem set GDAL_DIR=%PROGRAMFILES%\GDAL353
rem call "%GDAL_DIR%\GDALShell.bat"


rem GDAL integrated into qGis
rem -------------------------------------------------------------------

rem Here Change qGis directory
set QGIS=%PROGRAMFILES%\QGIS 3.34.11
set GDAL_DIR=%QGIS%\bin
set GDAL_DATA=%GDAL_DIR%\apps\gdal\share\gdal
set GDAL_DRIVER_PATH=%QGIS%\apps\gdal\lib\gdalplugins
set PROJ_LIB=%QGIS%\share\proj

rem GDAL Commen
rem -------------------------------------------------------------------

echo GDAL_DIR=%GDAL_DIR%
echo GDAL_DATA=%GDAL_DATA%
echo GDAL_DRIVER_PATH=%GDAL_DRIVER_PATH%
echo PROJ_LIB=%PROJ_LIB%

%SystemDrive%
cd "%GDAL_DIR%"
gdalinfo --version

rem Further commen variables
rem -------------------------------------------------------------------

rem set DEBUG=on
set DEBUG=off

set NETWORK=%PROCESSING_DIR%\%NAME%_Network.gpkg
set COMPOSITIONS=%GITHUB_DIR%\%NAME%\%NAME%_Compositions.geojson
set SEGMENTS=%GITHUB_DIR%\%NAME%\%NAME%_Segments.geojson
