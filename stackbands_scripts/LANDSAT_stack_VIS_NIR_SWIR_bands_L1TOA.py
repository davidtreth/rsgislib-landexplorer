# David Trethewey
#
# LANDSAT Bands Stacker
# Uses visible, NIR, SWIR1, SWIR2 bands (not including PAN)
# Should work with Landsat 5, 7, 8 images
#
# Converts GeoTIFF files of each band to single stacked file
# This version assumes the level 1 products as a starting point
# i.e. Top of Atmosphere rather than Level 2 surface reflectance
# this version does not include the cirrus band for Landsat 8
# in the output stack
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
    tifFileList = [f for f in dirFileList if f[-4:].lower() =='.kea']
tifFileList.sort()
# if this is a Landsat 8 image the third character of the filename is "8"
if "8" in tifFileList[0][:3]:
# select only bands 1-7
# this includes the 'coastal' band 1, but not the panchromatic
    bands = '1234567'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in bands)and(f[-6]=='B')]
    bandNamesList = ["Coastal", "Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2"]
# if this is a Landsat 7 or 5 image the third character of the filename is "7" or "5"
if "7" in tifFileList[0][:3] or "5" in tifFileList[0][:3]:
    # if this is a Landsat 5 or 7 image
    # select bands 1 to 5 and 7, excluding thermal IR band 6
    bands = '123457'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in '123457')and(f[-6]=='B')or((f[-6] in '123457')and(f[-7]=='B'))]
    bandNamesList = ["Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2"]
    
fileName = Bands_VIS_NIR_SWIR_FileList[0][:-7]

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
