# David Trethewey
#
# convert all .tiff? or .TIF files 
# in the current directory to .kea files
# using GDAL 
#
# Assumptions:
#
# the Level 1 GeoTIFF files are in the current directory
# that this script is being run from
#
#
#  
# imports
import os.path
import sys

# image list
# find all *.TIF files in the current directory
directory = os.getcwd()
dirFileList = os.listdir(directory)
# print dirFileList

tifFileList = [f for f in dirFileList if ((f[-4:].lower() =='.tif')or(f[-5:].lower() == '.tiff'))]

#output format (GDAL code)
outFormat = 'KEA'

for t in tifFileList:
    if t[-5:] == '.tiff':
        gdaltranscmd = "gdal_translate -of "+outFormat+" "+t+" "+t[:-5]+".kea"
    else:
        gdaltranscmd = "gdal_translate -of "+outFormat+" "+t+" "+t[:-4]+".kea"
    print(gdaltranscmd)
    os.system(gdaltranscmd)
