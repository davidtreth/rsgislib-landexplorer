rsgislib-landexplorer
Created by David Trethewey

A set of Python scripts for data exploration based on geotagged photos,
and (currently) Landsat images - at present certain things are hard coded so
that it expects a Landsat 7 or 8 image. Landsat 5 should work as well.

At this stage it is a big rough and ready so don't be suprised if something
doesn't work.

The scripts use the Remote Sensing and GIS python library: http://www.rsgislib.org
Please find information there on how to install and configure it, either there
or on Dan Clewley's blog at http://spectraldifferences.wordpress.com/
This program also makes use of the ImageMagick convert by using the shell, so will
only work on Linux.

The main script is 'readLandCoverGRPs.py' which takes an input file containing
the image filenames and their coordinates in a semicolon separated .csv,
and optionally a Landsat image.

I had been using Pythom Imaging Library/Pillow to read the ground reference point jpgs directly,
but then had trouble with it after I broke something in the python packages,
the code as it currently is uses the workaround of converting the input files
to PNG files and putting them in a subfolder 'png/'

the getGPS_folder_pexif.py script uses pexif https://github.com/bennoleslie/pexif
to read GPS data from already geotagged images and output to console a file containing
their filenames, latitudes and longitudes separated by semicolons.

The usage is to navigate to the folder of the input geotagged image files then run:
'python getGPS_folder_pexif.py > filecoords.csv' redirecting to a csv file which then
forms the input of readLandCoverGRPs.py:

python readLandCoverGRPs.py -i <coords.csv> [-s <landsat_scene>] [-u <utmzone>]

The Landsat scene should be a layerstack GDAL compatible file containing bands 1-5
and 7 for LS5/7 or bands 1-7 for LS8.

By default the program creates output png files in the 'outputplots/' folder

I have included some example data in the 'exampledata' folder with some images
from my MSc course fieldtrips and a subset of a Landsat7 scene of mid-Wales.

Update 09-05-16:
there is now a wrapper script run_readLandCover.py that can do conversion to resized png files, extraction of geotags from geotagged images, and currently calls readLandCoverGRPs.py twice, once in the system context and once in miniconda (this should hopefully no longer be necessary if I've sorted out my miniconda installation...)

python run_readLandCover.py -i  <coords.csv> [-s <landsat_scene>] [-u <utmzone>] [--makepng] [--extractgeo]

if --makepng is used, it will resize using the script resize_and_convertpng.py to 400px width, and if --extractgeo, it will call the getGPS_folder_pexif.py script to extract the geotags from the file into <coords.csv> - which need not exist beforehand in this case, but does need to be specified after the -i. 

