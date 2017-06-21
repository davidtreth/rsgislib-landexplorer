# David Trethewey
#
# Sentinel2 Band labeller
# Uses visible, NIR, SWIR bands
# 
# Assumptions:
#
# the image has been been downloaded as a Level2 atmosphere corrected image
# from scihub.copernicus.eu/dhus/processed
# and resampled in Sentinel Toolbox to a 10m resolution file as a GeoTIFF
# or KEA (after using gdal_translate to
# convert the rather enormous GeoTIFF that comes out of resampling the Level 2A product
#
# assume that this file is in the directory
# that this script is being run from
#
# there is only one Sentinel2 scene in the directory
# and no other .tif or .kea files
#  
# take the 1st 11 bands which are:
# 1 = B1 (coastal 443nm)
# 2 = B2 (blue 490nm)
# 3 = B3 (green 560nm)
# 4 = B4 (red 665nm)
# 5 = B5 (red edge 705nm)
# 6 = B6 (red edge 740nm)
# 7 = B7 (red edge 783nm)
# 8 = B8 (NIR broadband 842nm)
# 9 = B8a (NIR narrowband 865nm)
# 10 = B11 (SWIR 1610nm)
# 11 = B12 (SWIR 2190nm)

# there are other bands for things like AOT (optical thickness),  WVP (water vapour %)
# cloud probability, snow probability
# scenecclassification etc. but I need to be careful about ordering
# so don't label them yet

# imports
import rsgislib
import rsgislib.imageutils
import os.path
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--res", type=int, help='resolution - 10 or 20')
args = parser.parse_args()

if args.res not in [10, 20]:
    print("resolution not specified, assuming 10m")
    resol = 10
else:
    resol = args.res
    
# image list
# find all *.tif and *.kea files in the current directory
directory = os.getcwd()
dirFileList = os.listdir(directory)
# print dirFileList

tifFileList = [f for f in dirFileList if (f[-4:].lower() in ['.tif', '.kea'])]

#bands = "B23456788a1112"
bandNamesList = ["B1Coast443nm", "B2Blue490nm", "B3Green560nm", "B4Red665nm",
                 "B5NIR705nm", "B6NIR740nm", "B7NIR783nm", "B8NIR_broad842nm",
                 "B8A_NIR865nm", "B11_SWIR1610nm", "B12_SWIR2190nm"]
# this is intended for the product downloaded as the Level 2A atmosphere corrected
# and resampled to 10m within Sentinel Toolbox
# to do, make sure it is clear what order the rest of the bands are in before including
#                "#WVP", "AOT", "SceneClass", "Cloud", "Snow"]
bandInts = [i+1 for i in range(len(bandNamesList))]

for infile in tifFileList:
#if len(tifFileList) > 1:
#    print("warning, more than 1 potential input .tif or .kea file:")
#    print(tifFileList)
    print("using inputfile {i}".format(i=infile))
    
    inputImage =  infile
    fileNameBase = inputImage[:-4]



    #output file name
    # outputImage = fileNameBase + '_'+bands+'_stack.kea'

    #output format (GDAL code)
    outFormat = 'KEA'
    outType = rsgislib.TYPE_32UINT

    # select bands using rsgislib 
    #rsgislib.imageutils.selectImageBands(inputImage, outputImage, outFormat, outType, bandInts)
    # instead of creating new image, set band names in this image
    rsgislib.imageutils.setBandNames(inputImage, bandNamesList)
    # stats and pyramids
    rsgislib.imageutils.popImageStats(inputImage,True,0.,True)

