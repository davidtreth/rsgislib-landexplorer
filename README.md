rsgislib-landexplorer
Created by David Trethewey

A set of Python scripts for data exploration based on geotagged photos,
and Landsat or Sentinel 2 images.
A Landsat 7 or 8 image, Landsat 5 or Sentinel 2A/B images should work.

Utility scripts
===============

Stacking
========
Scripts for stacking the individual bands to an image stack are put in the stackbands_scripts/ folder

Scripts for converting all GeoTIFFs in a folder to KEA are in the convertKEAscripts/ folder.

Conversion from GeoTIFF to KEA
==============================
convertallTIFstoKEA.py: does exactly what the filename says, converting all GeoTIFF files in the
directory the program is run to KEA files by os.system() calling gdal_translate.

Landsat_convertallTIFstoKEA_createMTL_kea.py: this program assumes it is being run from a Landsat scene folder
and converts the band .TIF files to .kea and creating a new metadata file based on the *MTL.txt file
*MTL_kea.txt so that it refers to the .kea rather than .TIF files. This can be useful for running arcsi
atmospheric correction.

None of these scripts delete the original TIF files automatically.

Atmosphere correction of Sentinel 2
===================================
For L1C Sentinel 2 images, it is better to use SNAP
(Sentinel 2 toolbox) to make a layerstacked GeoTIFF so that the result is
georeferenced and atmosphere corrected in the sen2cor plugin.
This program assumes this is then converted to KEA format

There is now a facility to download L2A already preprocessed to Level 2 surface reflectance
from https://scihub.copernicus.eu
In this case it is still necessary to resample to either 10m, 20m or 60m.

At this stage it is a big rough and ready so don't be suprised if something
doesn't work. In particular, as of 18-06-2017 I still have to revise the Sentinel 2
stacking and band-naming scripts to make sure they get the band ordering right

The scripts use the Remote Sensing and GIS python library: http://www.rsgislib.org
Please find information there on how to install and configure it, either there
or on Dan Clewley's blog at http://spectraldifferences.wordpress.com/
This program also makes use of the ImageMagick convert by using the shell, so will
only work on Linux.



Extracting Geotags from images
==============================
the getGPS_folder_pexif.py script uses pexif https://github.com/bennoleslie/pexif
to read GPS data from already geotagged images and output to console a file containing
their filenames, latitudes and longitudes separated by semicolons.

The usage is to navigate to the folder of the input geotagged image files then run:
'python getGPS_folder_pexif.py > filecoords.csv' redirecting to a csv file which then
forms the input of readLandCoverGRPs.py

aside - I do not have a camera which can automatically geocode images so I
take a separate GPS device with me, and currently use the software Darktable to geotag.
The software Viking (which is available also on Windows) could also be used.


The main program of RSGISlib Land Explorer
==========================================
The main script is 'readLandCoverGRPs.py' which takes an input file containing
the image filenames and their coordinates in a semicolon separated .csv,
and optionally a Landsat or Sentinel 2 image.

to be revised once I sort out my conda packages installation....

I had been using Python Imaging Library/Pillow to read the ground reference point jpgs directly,
but then had trouble with it after I broke something in the python packages,
the code as it currently is uses the workaround of converting the input files
to PNG files and putting them in a subfolder 'png/'

The usage of the program is

python readLandCoverGRPs.py -i <coords.csv> [-s <landsat_scene>] [-u <utmzone>] [-a] [-b8]

The Landsat scene should be a layerstack GDAL compatible file containing bands 1-5
and 7 for LS5/7 or bands 1-7 for LS8.

By default the program creates output png files in the 'outputplots/' folder

I have included some example data in the 'exampledata' folder with some images
from my MSc course fieldtrips and a subset of a Landsat7 scene of mid-Wales.

Update 09-05-16:
there is now a wrapper script run_readLandCover.py that can do conversion to resized png files, extraction of geotags from geotagged images, and currently calls readLandCoverGRPs.py twice, once without specifying the scene (to generate the shapefiles of the points and areas around them), and once with it

python run_readLandCover.py -i  <coords.csv> [-s <landsat_scene>] [-u <utmzone>] [--makepng] [--extractgeo] [-a]

if --makepng is used, it will resize using the script resize_and_convertpng.py to 400px width, and if --extractgeo, it will call the getGPS_folder_pexif.py script to extract the geotags from the file into <coords.csv> - which need not exist beforehand in this case, but does need to be specified after the -i. 

if -a is used, it expects a L2A Sentinel product generated within sen2cor by the user rather than a stack of the raw images (L1C).

if -b8 is used, it expects a L2A Sentinel product downloaded ready-made by ESA Copernicus Hub and only resampled in SNAP - there is a difference in filenames which causes band 8A to be confused whether it should appear at the end or between band 8 or 9.