# Introduction

This repository holds a network topology about **backcountry ski routes of the Alps**. Each region consists of two [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) files:
1. Segments: A collection of LineString features with a segment id.
2. Compositions: A collection of routes with attributes and a list of segment id's.

Goals:
* Complete set of ski routes throughout the whole Alps.
* High quality standards.
* Compliance with the requirements of nature conservation.
* OpenData (Medium Term Goal)

Remarks:
* Despite the formal definition of the format [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) it is possible to store the EPSG code in the node **crs**. See chapter 4 of [RFC_7946](https://datatracker.ietf.org/doc/html/rfc7946).
* In order to support change-tracking, the coordinate precision must be set to two decimal digits.

# Regions

## 1. France
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=2154.

**Issuer**: All data of this folder are created and maintained by the [Petzl Foundation](https://www.petzl.com) in cooperation with the [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Creative Commons: [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). Suggestion for the attribution: _The ski routes are created and maintained [Petzl Foundation](https://www.petzl.com) in cooperation with the 
[Skitourenguru GmbH](https://www.skitourenguru.com)_.

**Caution**: The geometry of this data is highly abstracted, don't use it without the requiered smoothing. The folder [Derived Ski routes of France](https://download.skitourenguru.com/public/License.html) holds a smoothed version of the data (collection and network).

## 2. Switzerland
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=21781.

**Issuer**: All data of this folder were derived from the [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808), published by [Swisstopo](https://www.swisstopo.ch) in cooperation with the [Swiss Alpine Club](https://www.sac-cas.ch).

**License**: [Open Geo Data (OGD) License of Swisstopo](https://www.swisstopo.admin.ch/de/nutzungsbedingungen-kostenlose-geodaten-und-geodienste).

**Caution**: The data only contains the subset of ski routes that fulfill the quality requirements of Skitourenguru. For the complete dataset see [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808).

**Remark**: EPSG will eventually be changed from 21781 to 2056.

## 3. Austria
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31287.

**Issuer**: [Österreichischer Alpenverein](https://www.alpenverein.at).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 4. Germany
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=31468.

**Issuer**:  [Deutcher Alpenverein](https://www.alpenverein.de/).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 5. Italy
**Format**: [GeoJson](https://gdal.org/en/stable/drivers/vector/geojson.html) in EPSG=32632.

**Issuer**: [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Private license by Skitourenguru GmbH. Skitourenguru GmbH permits the usage of the data for private purpose. Aks the consent of Skitourenguru GmbH if you want to re-publish the data respectivly if you want to derive data from the raw data.

**Remark**: Skitourenguru is looking for a person willing to complete the data set in Italy. 

Requiered skills: 
* Experience with backcountry skiing
* Practical knowledge about backcountry areas in Italy
* Cartographic knowledge
* Understanding of avalanche terrain
* Affinity to IT
* If possible experience with qGis
* Open-minded
* Willing to work in a team 

## 6. Slovenia
tbd

# Disclaimer
While we strive to provide accurate and up-to-date information, we cannot guarantee the completeness or correctness of the data presented. The data issuers assume no guarantee and therefore no liability for the accuracy of the data in this repository.

# Tools
In order to edit ski routes within a network topology, two tools were developped:
1. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer): A qGis plugin to edit routes within a network topology.
2. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/): A SQL based method to edit routes within a network topology.

# Github

## 1. Intro
**Git** is a **version control software system** that is capable of managing versions of source code or data. It is often used to control source **code** or source **data** by participants who are developing the code or data collaboratively. Today, Git is the de facto standard version control system. 

**GitHub** is is a proprietary developer platform that allows developers to create, store, manage, and share **code** resp. **data**. It is the world's largest source code host as of June 2023. Since 2018 its owned by Microsoft.

* An intro to the purpose and structure of Git: [Video](https://www.youtube.com/watch?v=e9lnsKot_SQ)
* Installation and first commands: [Video](https://www.youtube.com/watch?v=r8jQ9hVA2qs)

## 2. Install a GIT client

Windows:
Install [Git](https://git-scm.com/downloads/win)

Accept all default values, ecept one: **Override the default branch name...** (see second video).

## 3. Clone Repo

Open a Git prompt and change to the parent dir of project:

```
cd D:\Local\Github
git clone https://github.com/skitourenguru/Routes.git
```

## 4. Register your id

Open a Git prompt

```
git config --global user.name myName
git config --global user.email myEmail@myEmail.com
```

## 5. Useful GIT commands

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

# Contact
On [https://www.skitourenguru.com](https://www.skitourenguru.com) under **about**.

