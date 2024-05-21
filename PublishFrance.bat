@echo off
setlocal enabledelayedexpansion

:Step1
echo ******************************************************************
echo 1. Update git
echo ******************************************************************
echo .


rem Git commands must be here before dir is changed
git pull

for /f "Delims=" %%a In ('git rev-parse HEAD') do set MYREVISION=%%a
echo MYREVISION=%MYREVISION%

for /f "Delims=" %%a In ('git tag --points-at HEAD') do set TAG=%%a

if defined TAG (
    echo TAG
) else (
    echo Last commit has no tag
)

:Step2
echo ******************************************************************
echo 2. Prepare Envirnoment Variables
echo ******************************************************************
echo .

rem set GDAL_DIR=%PROGRAMFILES(x86)%\GDAL
set GDAL_DIR=%PROGRAMFILES%\GDAL
echo GDAL_DIR=%GDAL_DIR%
%SystemDrive%
cd "%GDAL_DIR%"
call "%GDAL_DIR%\GDALShell.bat"
cd "%GDAL_DIR%"
gdalinfo --version

set WORKING_DIR=%~dp0
set WORKING_DIR=%WORKING_DIR:~0,-1%
echo WORKING_DIR=%WORKING_DIR%

set NAME=France
set REGION_SHORT_NAME=FR

rem User name of private computer of Guenter
if "%USERNAME%" == "james" (
	set GEO_TOOL=D:\Secure\Code\SkitourenguruBackend\GeoToolsCmd\bin\Release\net6.0\GeoToolsCmd.exe
	set COMPOSITION=%WORKING_DIR%\France\France_Compositions.geojson
	set SEGMENTS=%WORKING_DIR%\France\France_Segments.geojson
	set RESULT_DIR=D:\Secure\GPS\Projekte\Switzerland\ART\Skitourenguru\FR\segments
	set GRASSTOOL=C:\Program Files\QGIS 3.22.11\bin\Grass78.bat
	set ZIP_TOOL=C:\Program Files\7-Zip\7z.exe
	set TERRAIN_DIR=D:\Secure\GPS\Projekte\Switzerland\ART\Skitourenguru\%REGION_SHORT_NAME%\terrain
	set MODEL=D:\Secure\GPS\Projekte\Switzerland\ART\Design\Modell_V3.0\Results\Current\FootSectionModel\ModelCoefficients.csv
	set MAPSERVER_DIR=\\192.168.1.12\gis\skitourenguru\vector
	set PUBLIC_DIR=D:\Temp
	for /f "tokens=1-3 delims=. " %%a in ('date /t') do (set MYDATE=%%c%%b%%a)
)

rem User name of server (CALC)
if "%USERNAME%" == "Administrator" (
	set GEO_TOOL=C:\Skitourenguru2\Exe6.0\GeoToolsCmd.exe
	set COMPOSITION=%WORKING_DIR%\France\France_Compositions.geojson
	set SEGMENTS=%WORKING_DIR%\France\France_Segments.geojson
	set RESULT_DIR=C:\Skitourenguru2\FR\segments
	set GRASSTOOL=C:\Program Files\QGIS 3.22.16\bin\Grass78.bat
	set ZIP_TOOL=C:\Program Files\7-Zip\7z.exe
	set TERRAIN_DIR=C:\Skitourenguru2\FR\terrain
	set MODEL=C:\Skitourenguru2\FR\model\FootSections_ModelCoefficients.csv
	set MAPSERVER_DIR=\\192.168.1.12\gis\skitourenguru\vector
	set PUBLIC_DIR=\\SKITOURENGURU\public
	for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (set MYDATE=%%c%%b%%a)
)

rem User name of VirtualBox of Ulysse
if "%USERNAME%" == "ulysse" (
	set GEO_TOOL=
	set COMPOSITION=
	set SEGMENTS=
	set RESULT_DIR=
	set GRASSTOOL=
	set ZIP_TOOL=	
	set TERRAIN_DIR=
	set MODEL=
	rem set MAPSERVER_DIR=
	rem set PUBLIC_DIR=
	for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (set MYDATE=%%c%%b%%a)
)

if "%1"=="NOTEST" (
	set TEST=0
) else (
	set TEST=1
)
echo TEST=%TEST%

set LOG_FILE=%TEMP%\TopoMap_%MYDATE%.log
echo LOG_FILE=%LOG_FILE%
del /q "%TEMP%\TopoMap_*.log"

:Step3
echo .
echo ******************************************************************
echo 3. Play
echo ******************************************************************



:Step4
echo .
echo ******************************************************************
echo 4. Parameter settings
echo ******************************************************************

set SOURCE_EPSG=2154
set TARGET_EPSG=3857

set RESAMPLING_DIST=10

set BAND_WIDTH=20

rem Description = "If a foot section is shorter then minDeleteLength, it will be deleted
set MIN_DELETE_LENGTH=30

rem Description = "A foot section is expanded to minExpansionLength, if its shorter
set MIN_EXPANSION_LENGT=100

rem Description = "If a gap between two foot section is shorter then minGapLength, they will be merged
set MIN_GAP_LENGTH=100

rem myAsymmetricFactor=1
rem pThreashold=0.184021
rem 
rem       positives negatives
rem true      16047   1879373
rem false     15632     15632
rem 
rem myAsymmetricFactor=2
rem pThreashold=0.1183014
rem 
rem       positives negatives
rem true      19096   1869839
rem false     25166     12583
rem 
rem myAsymmetricFactor=3
rem pThreashold=0.09101105
rem       positives negatives
rem true      20547   1861608
rem false     33397     11132
rem 
rem myAsymmetricFactor=4
rem pThreashold= 0.07603073
rem       positives negatives
rem true      21529   1854404
rem false     40601     10150
rem 
rem 
rem myAsymmetricFactor <- 5
rem pThreashold=0.06578827
rem       positives negatives
rem true      22223   1847724
rem false     47281      9456

set THREASHOLD=0.065



:Step5
echo .
echo ******************************************************************
echo 5. Network to collection
echo ******************************************************************

%GEO_TOOL% /franceRouteConversionTool "%COMPOSITION%" "%SEGMENTS%" "%RESULT_DIR%" "" "%RESULT_DIR%\%NAME%_Raw.sqlite" 2154 1 1 ""

:Step6
echo .
echo ******************************************************************
echo 6. Smooth segments
echo ******************************************************************
echo .

set SMOOTHED_SEGMENTS=%RESULT_DIR%\%NAME%-Alpes-Segments-Smoothed.sqlite

rem set SMOOTH_COMMANDS=method=hermite threshold=5 angle_thresh=1;method=reumann threshold=3;method=chaiken threshold=5;method=reumann threshold=1
rem set SMOOTH_COMMANDS=method=chaiken threshold=5;method=reumann threshold=3;method=hermite threshold=10 angle_thresh=1;method=reumann threshold=1
set SMOOTH_COMMANDS=method=chaiken threshold=5 iterations=3;method=reumann threshold=1

%GEO_TOOL% /lineSmoothingTool "%GRASSTOOL%" "%SEGMENTS%" "%SMOOTHED_SEGMENTS%" "%SMOOTH_COMMANDS%" %SOURCE_EPSG%

:Step5
echo .
echo ******************************************************************
echo 5. Network to collection
echo ******************************************************************

%GEO_TOOL% /franceRouteConversionTool "%COMPOSITION%" "%SMOOTHED_SEGMENTS%" "%RESULT_DIR%" "" "%RESULT_DIR%\%NAME%_Smoothed.sqlite" 2154 1 1 ""

:Step8
echo .
echo ******************************************************************
echo 8. Create foot sections
echo ******************************************************************
echo .

set RESAMPLED_SEGMENTS=%RESULT_DIR%\%NAME%-Alpes-Resampled%RESAMPLING_DIST%.sqlite
set FOOT_SECTIONS=%RESULT_DIR%\%NAME%-Alpes-FootSections.sqlite

%GEO_TOOL% /lineResamplingTool "%SMOOTHED_SEGMENTS%" "%RESAMPLED_SEGMENTS%" %RESAMPLING_DIST% %SOURCE_EPSG%
%GEO_TOOL% /footSectionTool "%RESAMPLED_SEGMENTS%" "%TERRAIN_DIR%\Slope.tif" "%TERRAIN_DIR%\Fold.tif" "%TERRAIN_DIR%\Dem.tif" "%TERRAIN_DIR%\Terrain_MaxVelocity.tif" "%FOOT_SECTIONS%" "%MODEL%" "id" %SOURCE_EPSG% %RESAMPLING_DIST% %BAND_WIDTH% %MIN_DELETE_LENGTH% %MIN_EXPANSION_LENGT% %MIN_GAP_LENGTH% %THREASHOLD%

:Step9
echo .
echo ******************************************************************
echo 9. Insert foot sections into segments
echo ******************************************************************
echo .

set DISTRICTS=%RESULT_DIR%\MeteoFrance_Massifs.sqlite
set MERGED_SEGMENTS=%RESULT_DIR%\%NAME%-Alpes-Segments-Smoothed-FootSectionsIncluded.sqlite
set MERGED_SEGMENTS_QML=%RESULT_DIR%\%NAME%-Alpes-Segments-Smoothed-FootSectionsIncluded.qml
%GEO_TOOL% /lineMergeTool "%SMOOTHED_SEGMENTS%" "%FOOT_SECTIONS%" "%MERGED_SEGMENTS%" "%DISTRICTS%" "id" "foot" "did" 2154

:Step10
echo .
echo ******************************************************************
echo 10. Create ZIP
echo ******************************************************************
echo .

set REVISION_FILE=%RESULT_DIR%\Revision.txt

if exist "%REVISION_FILE%" del "%REVISION_FILE%"
echo %MYDATE%;%MYREVISION% >"%REVISION_FILE%"

set TARGET_LOG_FILE=%RESULT_DIR%\Warnings.log
copy /y "%LOG_FILE%" "%TARGET_LOG_FILE%"


set ZIP_FILE=%RESULT_DIR%\%NAME%-Ski.zip
if exist "%ZIP_FILE%" del /F /Q "%ZIP_FILE%"

rem Add derived data
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%MERGED_SEGMENTS%"
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%MERGED_SEGMENTS_QML%"
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%RESULT_DIR%\%NAME%_Smoothed.sqlite"

rem Add also raw data
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%COMPOSITION%"
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%SEGMENTS%"

"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%TARGET_LOG_FILE%"
"%ZIP_TOOL%" a -tzip %ZIP_FILE% "%REVISION_FILE%"

if "%USERNAME%" == "ulysse" exit

:Step11
echo .
echo ******************************************************************
echo 11. Export segments (with foot sections) as shp file in TARGET_EPSG
echo ******************************************************************
echo .

set TARGET_MERGED_SEGMENTS=%MAPSERVER_DIR%\%NAME%_SegmentsWithFootSections_%TARGET_EPSG%.shp
set MY_COMMAND=ogr2ogr -s_srs EPSG:%SOURCE_EPSG% -t_srs EPSG:%TARGET_EPSG% -overwrite -select id,did,foot -f "ESRI Shapefile" "%TARGET_MERGED_SEGMENTS%" "%MERGED_SEGMENTS%"
echo MY_COMMAND=%MY_COMMAND%
%MY_COMMAND%

set MY_COMMAND=ogrinfo -sql "CREATE SPATIAL INDEX ON %NAME%_SegmentsWithFootSections_%TARGET_EPSG%" "%TARGET_MERGED_SEGMENTS%"
echo MY_COMMAND=%MY_COMMAND%
%MY_COMMAND%

:Step12
echo .
echo ******************************************************************
echo 12. Publish ZIP
echo ******************************************************************
echo .

if defined TAG (
	set ZIP_FILE=%PUBLIC_DIR%\%NAME%-Ski.zip
	echo copy /y "%ZIP_FILE%" "%PUBLIC_DIR%"
	copy /y "%ZIP_FILE%" "%PUBLIC_DIR%"
)

set BACKUP_ZIP_FILE=%PUBLIC_DIR%\%NAME%-Ski-%MYDATE%-%MYREVISION%.zip
echo copy /y "%ZIP_FILE%" "%BACKUP_ZIP_FILE%"
copy /y "%ZIP_FILE%" "%BACKUP_ZIP_FILE%"


echo copy /y "%TARGET_LOG_FILE%" "%PUBLIC_DIR%"
copy /y "%TARGET_LOG_FILE%" "%PUBLIC_DIR%"


if %TEST%==1 (
	pause
)