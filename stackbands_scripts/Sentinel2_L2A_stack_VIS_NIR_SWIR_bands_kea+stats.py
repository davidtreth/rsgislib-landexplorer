# David Trethewey 01-06-2016
#
# Sentinel2 Bands Stacker
# Uses visible, NIR, SWIR bands
# 
# Assumptions:
#
# the .jp2 files are in the current directory
# that this script is being run from
#
# there is only one Sentinel2 scene in the directory
# and no other jp2 files
#  
# Converts jp2 files of each band to single stacked file
#  
# imports
#
# NOTE - it may be better to produce a layerstacked GeoTIFF in
# the Sentinel2 toolbox / SNAP of the L2A image product
# since this will be appropriately georeferenced

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
# find all *.jp2 files in the current directory
directory = os.getcwd()
dirFileList = os.listdir(directory)
# print dirFileList

jp2FileList = [f for f in dirFileList if (f[-4:].lower()=='.jp2')]

if resol == 20:
    bands = ['02', '03', '04', '05', '06', '07', '11', '12', '8A']
    # Sentinel2 bands
    bandNamesList = ["B2Blue490nm", "B3Green560nm", "B4Red665nm", "B5NIR705nm", "B6NIR740nm",
                     "B7NIR783nm", "B11_SWIR1610nm", "B12_SWIR2190nm", "B8A_NIR865nm"]

elif resol == 10:
    bands = ['02', '03', '04', '08']
    bandNamesList = ["B2Blue490nm", "B3Green560nm", "B4Red665nm", "B8NIR_broad842nm"]


# identify the band number by counting backwards from the end in the filename
Bands_VIS_NIR_SWIR_FileList = [f for f in jp2FileList if (f[-10:-8] in bands)and(f[-11]=='B')]


Bands_VIS_NIR_SWIR_FileList = sorted(Bands_VIS_NIR_SWIR_FileList)

blue_image = Bands_VIS_NIR_SWIR_FileList[0]
fileNameBase = blue_image[:-11]


#output file name
outputImage = fileNameBase + 'B'+''.join(bands)+'_stack.kea'

#output format (GDAL code)
outFormat = 'KEA'
outType = rsgislib.TYPE_32UINT

# stack bands using rsgislib 
rsgislib.imageutils.stackImageBands(Bands_VIS_NIR_SWIR_FileList, bandNamesList, outputImage, None, 0, outFormat, outType)
# stats and pyramids
rsgislib.imageutils.popImageStats(outputImage,True,0.,True)

