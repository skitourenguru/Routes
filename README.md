# A: Introduction

This repository holds a network topology about **backcountry ski routes of the Alps**. Each region consists of two [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) files:
1. Segments: A collection of LineString features with a segment id.
2. Compositions: A collection of routes with attributes and a list of segment id's.

Goals:
* Complete set of ski routes throughout the whole Alps.
* High quality standards.
* Compliance with the requirements of nature conservation.
* OpenData (Medium Term Goal)

The exact data model description you find in the this [Tecnical Specification](https://github.com/skitourenguru/Routes/blob/main/Doc/Skitouring_Network_Specification_1.0.3.pdf).

Remarks:
* Despite the formal definition of the format [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) it is possible to store the EPSG code in the node **crs**. See chapter 4 of [RFC_7946](https://datatracker.ietf.org/doc/html/rfc7946).
* In order to support change-tracking, the coordinate precision must be set to two decimal digits.

# B: Regions

## 1. France (Region=3)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=2154.

**Issuer**: All data of this folder are created and maintained by the [Petzl Foundation](https://www.petzl.com) in cooperation with the [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Creative Commons: [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). Suggestion for the attribution: _The ski routes are created and maintained [Petzl Foundation](https://www.petzl.com) in cooperation with the 
[Skitourenguru GmbH](https://www.skitourenguru.com)_.

**Caution**: The geometry of this data is highly abstracted, don't use it without the requiered smoothing. The [qGis smooth function](https://docs.qgis.org/3.40/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#smooth) must be applied (ITERATIONS=4, OFFSET=0.25, MAX_ANGLE=180). The folder [Derived Ski routes of France](https://download.skitourenguru.com/public/License.html) holds a smoothed version of the data (collection and network).

## 2. Switzerland (Region=1)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=21781.

**Issuer**: All data of this folder were derived from the [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808), published by [Swisstopo](https://www.swisstopo.ch) in cooperation with the [Swiss Alpine Club](https://www.sac-cas.ch).

**License**: [Open Geo Data (OGD) License of Swisstopo](https://www.swisstopo.admin.ch/de/nutzungsbedingungen-kostenlose-geodaten-und-geodienste).

**Caution**: The data only contains the subset of ski routes that fulfill the quality requirements of Skitourenguru. For the complete dataset see [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808).

**Remark**: EPSG will eventually be changed from 21781 to 2056.

## 3. Austria (Region=2)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31287.

**Issuer**: [Österreichischer Alpenverein](https://www.alpenverein.at).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

**Remarks**:
- Holds also South Tyrol (This is not a political statement!)

## 4. Germany (Region=6)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31468.

**Issuer**:  [Deutcher Alpenverein](https://www.alpenverein.de/).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 5. Italy (Region=7)
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=32632.

**Issuer**: [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Private license by Skitourenguru GmbH. Skitourenguru GmbH permits the usage of the data for private purpose. Aks the consent of Skitourenguru GmbH if you want to re-publish the data respectivly if you want to derive data from the raw data.

**Remarks**: 
- South Tyrol is contained in Austria (This is not a political statement!)
- Skitourenguru is looking for a person willing to complete the data set in Italy. 

Requiered skills: 
* Experience with backcountry skiing
* Practical knowledge about backcountry areas in Italy
* Cartographic knowledge
* Understanding of avalanche terrain
* Affinity to IT
* If possible experience with qGis
* Open-minded
* Willing to work in a team 

## 6. Slovenia (Region=8)
tbd

# C: Disclaimer
While we strive to provide accurate and up-to-date information, we cannot guarantee the completeness or correctness of the data presented. The data issuers assume no guarantee and therefore no liability for the accuracy of the data in this repository.

# D: Digitizing Tools
## 1. Digitizing in a network
In order to edit ski routes within a network topology, two tools were developped:
1. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer): A qGis plugin to edit routes within a network topology.
2. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/): A SQL based method to edit routes within a network topology.

## 2. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer)
In the folder [Batch](https://github.com/skitourenguru/Routes/tree/main/Scripts/Batch) you find an import and an export script. They can be used to convert the **geojson files** to a **geopackage network** that can be edited by the [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer).

In order to make sure the script works follow theses steps:
1. Copy the script to an other directory anywhere on your harddisk (Reason: You don't want to change the files in the repository).
2. In **Settings.bat** choose your **working directories** and the **dataset** you want to work with.
3. In **Environment.bat** you must set your [GDAL](https://gdal.org/) path. As GDAL is contained in qGis, its the easiest solution just to adapt the qgis version number.
4. Now you can use the scripts **ImportFromGithubToGpkg.bat** and **ExportFromGpkgToGithub.bat**. You can open them with a Text-Editor to see what they are doing.

## 3. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/)
to be written

# E: Derived data
Skitourenguru processes daily the raw data contained in this repository and builds a [SQLite / Spatialite RDBMS](https://gdal.org/en/stable/drivers/vector/sqlite.html) file containing a **collection of routes covering the whole Alps**. The automatic process performs the following steps:
1. Where needed (France) the routes are smoothed.
2. The network is converted to a **route collection**.
3. The routes are reprojected to the EPSG 3035.
4. The names (start and stop) are simplified where needed (Switzerland).
5. Route identifiers are made unique by adding a region code at the end of the id. The region codes are documented in chapter B.
6. The regions are merged.
7. The routes are filtered.
8. Attributes are added (lit, wildlife, pop, adiff, sri).
9. The route collection is verified.
10. The vector file is converted into two raster formats.
11. Finally the results are "published" on the Internet:

[Alps as Vector (SQLite / Spatialite RDBMS)](https://download.skitourenguru.com/routes/Alps.sqlite)

[Alps as Raster (RMaps format)](https://download.skitourenguru.com/routes/AP_SG_RT.sqlitedb)

[Alps as Raster (MapBox format)](https://download.skitourenguru.com/routes/AP_SG_RT.mbtiles)

**License**: 
The usage of this data is limited by the licenses documented in chapter B. The usage of this data for **private non-commercial purposes is allowed**. **All other usage is prohibited**. Be aware, that this dataset not only contains data from the sources described in chapter B, but also additional attributes generated by Skiturenguru. If you want to use this data in a commercial context or re-publish them, contact Skitourenguru (see chapter G).

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
git log -n 3

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
On [https://www.skitourenguru.com](https://www.skitourenguru.com) under **about**.

