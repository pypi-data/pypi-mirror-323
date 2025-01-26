# crossroads segmentation

**Crossroads segmentation** is a python tool that produces automatic segmentations of data from OpenStreetMap.

## Installation

With pip, use the following command line to install crseg:

* ```pip install crossroads-segmentation```

Dependancies:

* [OSMnx](https://osmnx.readthedocs.io/) that includes [NetworkX](https://networkx.org/) and [pandas](https://osmnx.readthedocs.io/).
* [argparse](https://docs.python.org/3/library/argparse.html)

## How it works

The computation uses both geometric and semantic information to identify and segment crossroads.

### Identify streets and classify nodes

<img src="images/segmentation-step1.png" width="300px" alt="">

### Build elementary intersections

<img src="images/segmentation-step2.png" width="300px" alt="">

### Merge intersections by proximity

<img src="images/segmentation-step3.png" width="300px" alt="">

### Merge intersections using multiple connectivity^

<img src="images/segmentation-step4.png" width="300px" alt="">

### Identify branches

<img src="images/segmentation-step5.png" width="300px" alt="">


A paper presenting the algorithms implemented in this tool has been accepted at the AGILE 2022 conference:

* Favreau, J.-M. and Kalsron, J., *[What are intersections for pedestrian users?](https://agile-giss.copernicus.org/articles/3/4/2022/)*, in proceedings of the 25th AGILE International Conference on Geographic Information Science, Vilnius, Lithuania, 2022. ([presentation](https://github.com/jmtrivial/crossroads-segmentation/raw/master/presentation/JM%20Favreau%20-%20AGILE2022%20-%20presentation%20-%20What%20are%20intersections%20for%20pedestrian%20users.pdf)).

This tool has been also be presented at [SOTM-fr](https://sotm2022.openstreetmap.fr/) 2022.



## Usage

If you installed crossroads-segmentation using pip, a console script is now available using ```get_crossroad_segmentation```. A slightly more complete version is available in the examples folder (```PYTHONPATH=$PWD examples/get-crossroad-segmentation.py```). You will find a complete segmentation of the possible parameters using the ```--help``` parameter.

This tool is using OSMnx to download OpenStreetMap data from the selected region. It uses a cache, stored in ```cache/``` directory. If a region has already been asked, it will use the cached data and not download it again. You can of course delete the cache directory to download again the data.

The location of the region can be choosen using coordinates (```--by-coordinates LAT LNG```) or using an predefined coordinate defined by a name in the example version (```--by-name NAME```). A radius (```-r VALUE```) with a default value of 150 meters can be adjusted to choose the size of the region to consider.

Several outputs are possible:

* to display the segmentation with all the crossings in the region (```--display-segmentation```), or only focussing on the main crossroad (```--display-main-crossroad```) closest to the input coordinate. This second display gives also the branches of the crossroad.
* to produce a text version of the selection (```--to-text```, ```--to-text-all```) in the standard output
* to produce a ```json``` file that contains all the detected crossroads (```--to-json-all FILENAME```) or only the main one (```--to-json FILENAME```). Branches are also contained in this output.


* 3 parameters (C0, C1 and C2) to drive the creation and merge of the crossroads (see associated publication)
* a maximum number of crossroads in a ring (```--max-cycle-elements NB```), with default value of 10 for the last step of the segmentation.


Several of these outputs (```--to-json```, ```--to-json-all```, ```--display-main-crossroad```, ```--to-geopackage```) can be adjusted using the parameter ```--multiscale``` to describe the small crossroad that has been merged to produce the large ones.

## Non regression tests

A very basic non regression test is provided in ```test``` directory. Usage:

* run first ```./regenerate_references.sh```
* run ```./test.sh``` each time you want to check for regressions

## Visual evaluation

A separated project is available to evaluate segmentation quality. See [crossroads-evaluation](https://github.com/jmtrivial/crossroads-evaluation).

## Examples


```./get-crossroad-segmentation.py --by-name POC1  --display-main-crossroad --multiscale```

![POC1](https://raw.githubusercontent.com/jmtrivial/crossroads-segmentation/master/images/POC1.png)


```./get-crossroad-segmentation.py --by-name obélisque  --display-segmentation -r 1000```

![R1000](https://raw.githubusercontent.com/jmtrivial/crossroads-segmentation/master/images/R1000.png)


