# David Trethewey
#
# LANDSAT Bands Stacker
# Uses visible, NIR, SWIR1, SWIR2 bands (not including PAN)
# Should work with Landsat 5, 7, 8 images
#
# Converts GeoTIFF files of each band to single stacked file
#
# this version works with the Landsat 8 images already downloaded preprocessed
# to Level 2surface reflectance
# see https://landsat.usgs.gov/landsat-surface-reflectance-high-level-data-products
#
# Assumes only one scene per directory
# imports
import rsgislib
import rsgislib.imageutils
import os.path
import sys

# image list
# find all *.TIF files in the current directory
directory = './'
dirFileList = os.listdir(directory)
tifFileList = [f for f in dirFileList if f[-4:].lower() =='.tif']
if len(tifFileList) == 0:
    # if they've been converted to .kea and the original tifs deleted
    tifFileList = [f for f in dirFileList if f[-4:].lower() =='.kea']
tifFileList.sort()
# if this is a Landsat 8 image the fourth character of the filename is "8"
if tifFileList[0][3] == "8": 
# select only bands 1-7
# this includes the 'coastal' band 1, but not the panchromatic
    bands = '1234567'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in bands)and(f[-12:-5]=='sr_band')]
    bandNamesList = ["Coastal", "Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2"]
# if this is a Landsat 7 image the fourth character of the filename is "7"
# Landsat 5 and 7 may not be currently available preprocessed to Level 2

if "7" in tifFileList[0][:4] or "5" in tifFileList[0][:4]:
    # if this is a Landsat 5 or 7 image
    # select bands 1 to 5 and 7, excluding thermal IR band 6
    bands = '123457'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in bands)and(f[-12:-5]=='sr_band')]
    bandNamesList = ["Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2"]

fileName = Bands_VIS_NIR_SWIR_FileList[0][:-10]

#output file
outputImage = fileName + '_B'+bands+'_stack.kea'
#output format
outFormat = 'KEA'
#outFormat = 'GTiff'
outType = rsgislib.TYPE_32UINT

# stack bands
rsgislib.imageutils.stackImageBands(Bands_VIS_NIR_SWIR_FileList, bandNamesList, outputImage, None, 0, outFormat, outType)
# stats and pyramids
rsgislib.imageutils.popImageStats(outputImage,True,0.,True)
