# A: Introduction

This repository holds a network topology about **backcountry ski routes of the Alps**. It serves as entry point of **ski route raw data** for Skitourenguru. 

**Caution**: Please be aware that this repository is under construction. It will be fully functional from the Spring 2026 on!

Each region consists of two [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) files:
1. Segments: A collection of LineString features with a segment id.
2. Compositions: A collection of routes with attributes and a list of segment id's.

Goals:
* Complete set of ski routes throughout the whole Alps.
* High quality standards.
* Compliance with the requirements of nature conservation.
* OpenData (Medium Term Goal)

The exact data model description you find in this [Technical Specification](https://github.com/skitourenguru/Routes/blob/main/Doc).

Remarks:
* Despite the formal definition of the format [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) it is possible to store the EPSG code in the node **crs**. See chapter 4 of [RFC_7946](https://datatracker.ietf.org/doc/html/rfc7946).
* In order to support change-tracking, the coordinate precision must be set to two decimal digits.

# B: Regions

## 1. Switzerland (RegionCode=1)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=21781.

**Issuer**: All data of this folder were derived from the [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808), published by [Swisstopo](https://www.swisstopo.ch) in cooperation with the [Swiss Alpine Club](https://www.sac-cas.ch).

**License**: [Open Geo Data (OGD) License of Swisstopo](https://www.swisstopo.admin.ch/de/nutzungsbedingungen-kostenlose-geodaten-und-geodienste).

**Caution**: The data only contains the subset of ski routes that fulfill the quality requirements of Skitourenguru. For the complete dataset see [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808).

**Remark**: EPSG will eventually be changed from 21781 to 2056.

## 2. Austria (RegionCode=2)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31287.

**Issuer**: [Österreichischer Alpenverein](https://www.alpenverein.at).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

**Remarks**:
- Holds also South Tyrol (This is not a political statement!)

## 3. France (RegionCode=3)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=2154.

**Issuer**: All data of this folder are created and maintained by the [Petzl Foundation](https://www.petzl.com) in cooperation with the [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Creative Commons: [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). Suggestion for the attribution: _The ski routes are created and maintained [Petzl Foundation](https://www.petzl.com) in cooperation with the 
[Skitourenguru GmbH](https://www.skitourenguru.com)_.

**Caution**: The geometry of this data is highly abstracted, don't use it without the requiered smoothing. The [qGis smooth function](https://docs.qgis.org/3.40/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#smooth) must be applied (ITERATIONS=4, OFFSET=0.25, MAX_ANGLE=180). The folder [Derived Ski routes of France](https://download.skitourenguru.com/public/License.html) holds a smoothed version of the data (collection and network).

## 4. Italy (RegionCode=6)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=32632.

**Issuer**: [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Private license by Skitourenguru GmbH. Skitourenguru GmbH permits the usage of the data for private purpose. Aks the consent of Skitourenguru GmbH if you want to re-publish the data respectivly if you want to derive data from the raw data.

**Remarks**: 
- South Tyrol is contained in Austria (This is not a political statement!)

**Help needed**
Skitourenguru is looking for a person willing to complete the data set in Italy. The work can be partly paid.

Requiered skills: 
* Experience with backcountry skiing
* Practical knowledge about backcountry areas in Italy
* Cartographic knowledge
* Understanding of avalanche terrain
* Affinity to IT
* If possible experience with qGis
* Open-minded
* Willing to work in a team 

Contact [Skitourenguru](https://www.skitourenguru.com) under **about** if you want to collaborate.

## 5. Germany (RegionCode=7)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31468.

**Issuer**:  [Deutcher Alpenverein](https://www.alpenverein.de/).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 6. Slovenia (RegionCode=8)
**Help needed**
Skitourenguru is looking for a person willing to digitalize ski routes in Slovenia. The work can be partly paid.

Requiered skills: 
* Experience with backcountry skiing
* Practical knowledge about backcountry areas in Slovenia
* Cartographic knowledge
* Understanding of avalanche terrain
* Affinity to Slovenia
* If possible experience with qGis
* Open-minded
* Willing to work in a team 

Contact [Skitourenguru](https://www.skitourenguru.com) under **about** if you want to collaborate.

# C: Derived data
Skitourenguru processes weekly (Monday 1:00h) the raw data contained in this repository and builds a [SQLite / Spatialite RDBMS](https://gdal.org/en/stable/drivers/vector/sqlite.html) file containing a **collection of routes covering the whole Alps**. The automatic process performs the following steps:
1. Where needed (France) the routes are smoothed: (Chaiken: 3 Interations, Threashold 5 m).
2. Simplification (Douglas: Theashold: 1 m).
2. The network is converted to a **route collection**.
3. The routes are reprojected to the EPSG 3035.
4. Geospatial filter
5. The names (start and stop) are simplified where needed (Switzerland).
6. Route identifiers are made unique by adding a region code at the end of the id. The region codes are documented in chapter B.
7. The regions are merged.
8. The routes are filtered by **length**, **target** end **type** (Skitour = 1).
9. Attributes are added (**lit**: A hint about literature, in particular the editor Panico, **wildlife**: Distance to next nature protection area, **pop**: A popularity indicator, **adiff**: A difficulty grade automatically derived from terrain properties, **sri**: Standard rating indicators about the avalanche risk for 10 typical avalanche bulletins). If you need to know more about these attributes, click on a route on [https://www.skitourenguru.com](https://www.skitourenguru.com).
10. The route collection is verified.
11. [Corridors](https://info.skitourenguru.ch/index.php/corridors) are created
12. The vector file is converted into two raster formats
13. Finally the results are "published" on the Internet:

[Alps as Vector](https://download.skitourenguru.com/routes/Alps.sqlite) in the [SQLite / Spatialite RDBMS](https://gdal.org/en/stable/drivers/vector/sqlite.html) format.

[Alps as Raster](https://download.skitourenguru.com/routes/AP_SG_RT.sqlitedb) in the [RMaps / Galileo](https://www.bluemarblegeo.com/knowledgebase/global-mapper/Formats/RMaps_SQLite_Database.htm) format.

[Alps as Raster](https://download.skitourenguru.com/routes/AP_SG_RT.mbtiles) in the  [MapBox-Tiles](https://github.com/mapbox/mbtiles-spec) format.

**License**: 
The usage of this data is limited by the licenses documented in chapter B. Otherwise, the following applies: The usage of this data for **private non-commercial purposes is allowed**. **All other usage is prohibited**. In particular its not allowed to create derivates of the data (see ND in chapter B). Be aware, that this dataset not only contains data from the sources described in chapter B, but also additional attributes generated by Skiturenguru. If you want to use this data in a commercial context or re-publish them, contact Skitourenguru (see chapter G).

# D: Disclaimer
While we strive to provide accurate and up-to-date information, we cannot guarantee the completeness or correctness of the data presented. The data issuers assume no guarantee and therefore no liability for the accuracy of the data in this repository.

# E: Digitizing Tools
## 1. Digitizing in a network
In order to edit ski routes within a network topology, two tools were developped:
1. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer): A qGis plugin to edit routes within a network topology.
2. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/): A SQL based method to edit routes within a network topology.

## 2. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer)
In the folder [Batch](https://github.com/skitourenguru/Routes/tree/main/Scripts/Batch) or [Bash](https://github.com/skitourenguru/Routes/tree/main/Scripts/Bash) you find an import and an export script. They can be used to convert the **geojson files** to a **geopackage network** that can be edited by the [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer).

### Windows (Batch)
In order to make sure the script works follow theses steps:
1. Copy the script to an other directory anywhere on your harddisk (Reason: You don't want to change the files in the repository).
2. In **Settings.bat** choose your **working directories** and the **dataset** you want to work with.
3. In **Environment.bat** you must set your [GDAL](https://gdal.org/) path. As GDAL is contained in qGis, its the easiest solution just to adapt the qgis version number.
4. Now you can use the scripts **ImportFromGithubToGpkg.bat** and **ExportFromGpkgToGithub.bat**. You can open them with a Text-Editor to see what they are doing.
5. Make sure that **Segments** and **Compositions** auto-set their id: Open **Attributes Form**, click on id and enter under **Default** the **Default value**: **maximum(id)+1**.

### Linux/MacOs (Bash)
1. Launch the script **ImportFromGithubToGpkg.sh** a first time, it will copy the settings file. Edit the **Settings.sh** file with the country name. 
2. Launch the script again, it will create the corresponding gpkg file inside the country folder. You normally don't need to run it again - but if for some reason you lose the gpkg files, run again the script **ImportFromGithubToGpkg.sh**. 
3. Add the layers to the project.
4. Make sure that **Segments** and **Compositions** auto-set their id: Open **Attributes Form**, click on id and enter under **Default** the **Default value**: **maximum(id)+1**.
5. Make some changes, and before committing your work, run the script **ExportFromGpkgToGithub.sh**. Commit and push.

***

Principally the **Compositions** layer has no geometry. However the plugin can also create geometries from the **Segments** and handle them during editing. That means whenever you change the geometry of a segment, all Compositions that use this geometry will update their geometry.
1. Open the Plugin and click on **Create Geometries**: This will create an in-memory layer. In the next steps we will substitute the layer **Compositions** of the **GPKG** with the newly created in-memory layer.
2. Right-Click on the in-memory Layer and click on **Make Permanent**.
3. Choose Format **GPKG**, the file **MyRegion_Network.gpkg** and the **Layer Composition**.
4. When you click on **OK** you will get asked about the desired overwriting behaviour. Choose **Overwrite Layer**.
5. You can now remove the old layer **MyRegion_Network - Composition** from the project by right clicking on it and **Remove Layer**.
6. Start the plugin after having made sure that configuration is correct.
7. In the Plugin configuration: Enable **Allow geometry creation** on the fly.

Remarks:
- If you want to manually update the geometry of the **Compositions** layer with **Update Geometry**, make sure the the layer **Compositions** is on editing.

## 3. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/)
to be written

# F: Github

## 1. Intro
**Git** is a **version control software system** that is capable of managing versions of source code or data. It is often used to control source **code** or source **data** by participants who are developing the code or data collaboratively. Today, Git is the de facto standard version control system. 

**GitHub** is is a proprietary developer platform that allows developers to create, store, manage, and share **code** resp. **data**. It is the world's largest source code host as of June 2023. Since 2018 its owned by Microsoft.

* An intro to the purpose and structure of Git: [Video](https://www.youtube.com/watch?v=e9lnsKot_SQ)
* Installation and first commands: [Video](https://www.youtube.com/watch?v=r8jQ9hVA2qs)

## 2. Install a GIT client

Windows:
Install [Git](https://git-scm.com/downloads/win)

Accept all default values, except one: **Override the default branch name...** (see second video).

On Windows open the search box and type **git**. Now you can start **Git CMD** and a command prompt opens. Alternatively you open a normal **command prompt** and check, if the command **git** is available (it should). Alternatively you can also work with **Git GUI**.

## 3. Clone Repo

Open a Git prompt and change to the parent dir of project:

```
cd D:\Local\Github
git clone https://github.com/skitourenguru/Routes.git
```

Remark:
* The path D:\Local\Github is an example. Thats the place where you want all your repositories to be located (parent directory)

## 4. Register your id

Open a Git prompt

```
git config --global user.name myName
git config --global user.email myEmail@myEmail.com
```

## 5. Daily work

Suppose you work on a file, like **ReadMe.md** or **Italy_Compositions.geojson**. Just use normally whatever tool you are used to. At a certain moment you want to **commit** and **push** the changes to the Github-Server.

Open a Git prompt 

```
// Make sure you are in the folder of your working dir
cd D:\Local\Github\Routes

// Make sure your local repository and the working dir are up-to-date
git pull

// First you commit: Changes are written to your local repository (a copy of the remote repository that is located on your computer)
git commit -m "Corrected the typo in the name of route with id=45" Italy/Italy_Compositions.geojson

// Second you push: Changes are written to the remote repository (on the Github-Server).
git push

```

Remarks:
* You can add also new files. Usually that won't be necessary. 
* In this example we worked on the **main** branch. Its also possible to work with branches. For the purpose of the current repository that won't be necessary.
* A good field of excercise is ReadMe.md. You can change typos or improve the docu. The file is written with [Markup-Down](https://en.wikipedia.org/wiki/Markdown) language. That's a very simple  markup language that allows formatting documents. Use a Text-Editor like [Notepad++](https://notepad-plus-plus.org/downloads/) to edit ReadMe.md. Start with simple changes.

## 6. Useful GIT commands

```
// Change a file
git commit -m "Create France_Smoothed.sqlite" PublishFrance.bat
git push

// Stage and commit all changes in dir including sub dir
git commit -am "I made many changes"
git push

// Remove a file
git rm TopoMap_20230726.log
git commit -m "Deleted log files"
git push

// Add a new file
git add France-Alpes/France-Alpes-Foot-Manipulation.gpkg
git commit -m "Added a new file"
git push

// Check on which branch we are
git branch

// Check, if there is something to be pushed
git diff --stat origin/main

// Delete local changes in workspace and update
git stash push --include-untracked
git stash drop
git pull

// Get the GUID of the head
git rev-parse HEAD
git rev-parse --short HEAD

// See history
git --no-pager log -n 100 --pretty=format:"%h %ad %s" --date=iso

// List last 10 commit statements of a particular file
git log --pretty=oneline -10 src/locale/it.ts

// Configures the output such as all results are displayed
git config --global core.pager cat
git log --merges -n 20 --pretty=oneline
git log --merges -n 20 --pretty=format:"%cs: %s"
git log --merges -n 20 --pretty=format:"%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset"
git log --merges -n 20 --pretty=format:"%cs: %s%b %n--------------------------------------------------------------"
git log --merges -n 20 --pretty=format:"%cs: %s --- %b"
git log --merges -n 20 --pretty=format:"%Cgreen%cs%Creset: %s --- %C(yellow)%b --- %C(red)%an"

// Checkout old version and go back to last version
git log -10
git checkout 3601638a0d558fe13e24c5a0abb37348ed7479f3
git checkout -

// Fetch a branch from the remote to the local repository
git fetch origin myBranch

// Fetch everything from the remote rep to the local rep
git fetch --all
git pull --all

// Display branch you are on
git rev-parse --abbrev-ref HEAD

// Get a syntax problem list for the whohle project
npx eslint . --ext .js,.vue

```

# G: Contact
If you want to notify an error or a remark about the routes data described in chapter B, contact us depending on the region:
1. France: randohiver@fondation-petzl.org
2. Switzerland: andreas.eisenhut@sac-cas.ch
3. Austria: [AlpenvereinAktiv](https://www.alpenvereinaktiv.com/de/kontakt.html)
4. Germany: [AlpenvereinAktiv](https://www.alpenvereinaktiv.com/de/kontakt.html)
5. Italy: [Skitourenguru](https://www.skitourenguru.com) under **about**.
6. Slovenia: tbd

For all other questions, contact [Skitourenguru](https://www.skitourenguru.com) under **about**.
