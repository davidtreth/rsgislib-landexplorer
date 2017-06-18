# David Trethewey
#
# LANDSAT Bands Stacker
# Uses visible, NIR, SWIR1, SWIR2 bands (not including PAN)
# this version will include the thermal infrared bands
# which are output to a separate stack of 2 (TIR1, TIR2)
#
# Should work with Landsat 5, 7, 8 images
# for Landsat 8 includes the Cirrus band in the stack
#
# 
# Assumptions:
#
# the Level 1 GeoTIFF files are in the current directory
# that this script is being run from
#
# there is only one Landsat scene in the directory
# and no other TIF files
#  
# Converts GeoTIFF files of each band to single stacked KEA file
# if GeoTiff output is desired change the line specifying the
# outFormat variable
#
# This version should also work if the GeoTIFFs have been converted
# to KEA files and the originals deleted
#
# This works with the Level 1 Top of Atmosphere files rather
# than Level 2 surface reflectance
# imports
import rsgislib
import rsgislib.imageutils
import os.path
import sys

# image list
# find all *.TIF files in the current directory
directory = os.getcwd()
dirFileList = os.listdir(directory)
# print dirFileList

tifFileList = [f for f in dirFileList if f[-4:].lower() =='.tif']
if len(tifFileList) == 0:
    # if no .tifs look for .kea files
    tifFileList = [f for f in dirFileList if f[-4:].lower() =='.kea']
# if this is a Landsat 8 image the third character of the filename is "8"
if "8" in tifFileList[0][:3]:
# select only bands 1-7
# this includes the 'coastal' band 1, but not the panchromatic
# and the cirrus (band 9 , i.e. band 8 in stack)
    bands = '12345679'
    # identify the band number by counting backwards from the end in the filename
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in bands)and(f[-6]=='B')]
    Bands_TIR_FileList = [f for f in tifFileList if (f[-6]=='1')and(f[-7]=='B')] #bands 10 and 11
    bandNamesList = ["Coastal", "Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2", "Cirrus_1.37"]
# if this is a Landsat 5 or 7 image

# if this is a Landsat 7 image the third character of the filename is "7"
# sometimes this can be the second character ?
if "7" in tifFileList[0][:3] or "5" in tifFileList[0][:3]:
    # select bands 1 to 5 and 7, excluding thermal IR band 6
    bands = '123457'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in '123457')and(f[-6]=='B')or((f[-6] in '123457')and(f[-7]=='B'))]
    bandNamesList = ["Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2"]

fileNameBase = Bands_VIS_NIR_SWIR_FileList[0][:-7]


TIRbandNamesList = ['TIR1', 'TIR2']

#output file name

outputImage = fileNameBase + '_B'+bands+'_stack.kea'
outputImageTIR = fileNameBase + '_B10_11_TIR_stack.kea'

#output format (GDAL code)
outFormat = 'KEA'
#outFormat = 'GTiff'
outType = rsgislib.TYPE_32UINT

# stack bands using rsgislib 
rsgislib.imageutils.stackImageBands(Bands_VIS_NIR_SWIR_FileList, bandNamesList, outputImage, None, 0, outFormat, outType)
rsgislib.imageutils.stackImageBands(Bands_TIR_FileList, TIRbandNamesList, outputImageTIR, None, 0, outFormat, outType)
# stats and pyramids
rsgislib.imageutils.popImageStats(outputImage,True,0.,True)
rsgislib.imageutils.popImageStats(outputImageTIR,True,0.,True)
