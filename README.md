# Introduction

This repository holds a network topology about **backcountry ski routes of the Alps**. Each region consists of two **geojson** files:
1. Segments: A collection of LineString features with a segment id.
2. Compositions: A collection of routes with attributes and a list of segment id's.

Goals:
* Complete set of ski routes throughout the whole Alps.
* High quality standards.
* Compliance with the requirements of nature conservation.
* OpenData (Medium Term Goal)

# Regions

## 1. France
**Issuer**: All data of this folder are created and maintained by the [Petzl Foundation](https://www.petzl.com) in cooperation with the [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Creative Commons: [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). Suggestion for the attribution: _The ski routes are created and maintained [Petzl Foundation](https://www.petzl.com) in cooperation with the 
[Skitourenguru GmbH](https://www.skitourenguru.com)_.

**Caution**: The geometry of this data is highly abstracted, don't use it without the requiered smoothing. The folder [Derived Ski routes of France](https://download.skitourenguru.com/public/License.html) holds a smoothed version of the data (collection and network).

## 2. Switzerland
**Issuer**: All data of this folder were derived from the [Ski-Routes](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/33090bf2-e8e5-4776-9f64-00d7a6170808), published by [Swisstopo](https://www.swisstopo.ch) in cooperation with the [Swiss Alpine Club](https://www.sac-cas.ch).

**License**: [Open Geo Data (OGD) License of Swisstopo](https://www.swisstopo.admin.ch/de/nutzungsbedingungen-kostenlose-geodaten-und-geodienste).

**Caution**: The data only contains the subset of ski routes that fulfill the quality requirements of Skitourenguru.

## 3. Austria
**Issuer**: [Österreichischer Alpenverein](https://www.alpenverein.at).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 4. Germany
**Issuer**:  [Deutcher Alpenverein](https://www.alpenverein.de/).

**License**: Private license till 14. October 2026. From 15. October 2026 on published under [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## 5. Italy
**Issuer**: [Skitourenguru GmbH](https://www.skitourenguru.com).

**License**: Private license by Skitourenguru GmbH. Skitourenguru GmbH permits the usage of the data for private purpose. Aks the consent of Skitourenguru GmbH if you want to re-publish the data respectivly if you want to derive data from the raw data.

**Remark**: Skitourenguru is looking for a person willing to complete the data set in Italy. Requiered skills: Experience with backcountry skiing, practical knowledge about backcountry areas in Italy, knowledge about avalanche terrain, cartographic knowledge, knowledge about qGis, open-minded. 

## 6. Slovenia
tbd

# Disclaimer
While we strive to provide accurate and up-to-date information, we cannot guarantee the completeness or correctness of the data presented. The data issuers assume no guarantee and therefore no liability for the accuracy of the data in this repository.

# Tools
In order to edit ski routes within a network topology, two tools were developped:
1. [Routes Composer](https://github.com/UlysselaGlisse/RoutesComposer): A qGis plugin to edit routes within a network topology.
2. [SAC Route Network Editor](https://github.com/andreglauser/sac-route-network-editor/): A SQL based method to edit routes within a network topology.

