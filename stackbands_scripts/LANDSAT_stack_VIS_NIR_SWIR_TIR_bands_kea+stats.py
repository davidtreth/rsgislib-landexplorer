# David Trethewey 23-05-2014
#
# LANDSAT Bands Stacker
# Uses visible, NIR, SWIR1, SWIR2 bands (not including PAN)
# Should work with Landsat 5, 7, 8 images
#
# Assumptions:
#
# the Level 1 GeoTIFF files are in the current directory
# that this script is being run from
#
# there is only one Landsat scene in the directory
# and no other TIF files
#  
# Converts GeoTIFF files of each band to single stacked file
#  
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

tifFileList = [f for f in dirFileList if ((f[-4:]=='.TIF')or(f[-4:]=='.tif'))]
# if this is a Landsat 8 image the third character of the filename is "8"
if tifFileList[0][2] == "8": 
# select only bands 1-7
# this includes the 'coastal' band 1, but not the panchromatic
# and the cirrus (band 9 , i.e. band 8 in stack)
    bands = '12345679'
    # identify the band number by counting backwards from the end in the filename
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in bands)and(f[-6]=='B')]
    Bands_TIR_FileList = [f for f in tifFileList if (f[-6]=='1')and(f[-7]=='B')] #bands 10 and 11

# if this is a Landsat 5 or 7 image

# if this is a Landsat 7 image the third character of the filename is "7"
# sometimes this can be the second character ?
if tifFileList[0][2] == "7" or tifFileList[0][1] == "7" or tifFileList[0][2] == "5" or tifFileList[0][1] == "5": 
    # select bands 1 to 5 and 7, excluding thermal IR band 6
    bands = '123457'
    Bands_VIS_NIR_SWIR_FileList = [f for f in tifFileList if (f[-5] in '123457')and(f[-6]=='B')or((f[-6] in '123457')and(f[-7]=='B'))]

Bands_VIS_NIR_SWIR_FileList = sorted(Bands_VIS_NIR_SWIR_FileList)
Bands_TIR_FileList = sorted(Bands_TIR_FileList)
fileNameBase = Bands_VIS_NIR_SWIR_FileList[0][:-4]

#bandNamesList = ['Band '+f[-5] for f in Bands_VIS_NIR_SWIR_FileList]
bandNamesList = ["Coastal", "Blue", "Green", "Red", "NIR", "SWIR1_1.6", "SWIR2_2.2", "Cirrus_1.37"]
#TIRbandNamesList = ['Band '+f[-6:-4] for f in Bands_TIR_FileList]
TIRbandNamesList = ['TIR1', 'TIR2']

#output file name
outputImage = fileNameBase + '_B'+bands+'_stack.kea'
outputImageTIR = fileNameBase + '_B10_11_TIR_stack.kea'
#outputImage = fileNameBase + '_B'+bands+'_stack.tif'
#outputImageTIR = fileNameBase + '_B10_11_TIR_stack.tif'

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
