# David Trethewey 01-06-2016
#
# Sentinel2 Bands Stacker
# Uses visible, NIR, SWIR bands
# 
# Assumptions:
#
# the image has been processed in SNAP / sen2cor
# and resampled to a 10m file as a GeoTIFF or KEA (after using gdal_translate to
# convert the rather enormous GeoTIFF that comes out of resampling the Level 2A product
#
# assume that this file is in the directory
# that this script is being run from
#
# there is only one Sentinel2 scene in the directory
# and no other .tif or .kea files
#  
# take the 1st 15 bands which are (I think):
# 1 = B2 (blue 490nm)
# 2 = B3 (green 560nm)
# 3 = B4 (red 665nm)
# 4 = B5 (red edge 705nm)
# 5 = B6 (red edge 740nm)
# 6 = B7 (red edge 783nm)
# 7 = B8 (NIR broadband 842nm)
# 6 = B8a (NIR narrowband 865nm)
# 9 = B11 (SWIR 1610nm)
# 10 = B12 (SWIR 2190nm)
# 11 = AOT
# 12 = WVP
# 13 = cloud
# 14 = snow
# 15 = sceneclassification

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

