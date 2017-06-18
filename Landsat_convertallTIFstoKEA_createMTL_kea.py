# David Trethewey 20-06-2014
#
# convert all .tif or .TIF files 
# in the current directory to .kea files
# using GDAL 
# Does not delete any TIF files
#
# Assumptions:
# the TIF files are in the current directory
# that this script is being run from
# GDAL is available with KEA support
#  
# Modifies any Landsat header *MTL.txt files so that
# arcsi.py works if you have compressed the 
# band .TIF files to .kea
# Does not overwrite original header
#
# imports
import os.path
import sys

def replaceGTIFF_kea(inputtext):
    outputtext = ""    
    for w in inputtext:
        w = w.replace("GEOTIFF","KEA")
        w = w.replace(".TIF",".kea")
        # this line should be unnecessary since Landsat MTL files use capital letters       
        # but just in case you have one that doesn't
        w = w.replace(".tif",".kea")
        outputtext += w
    return outputtext

# find all *.TIF files and *MTL.txt files in the current directory
directory = os.getcwd()
dirFileList = os.listdir(directory)
# print dirFileList
tifFileList = [f for f in dirFileList if ((f[-4:]=='.TIF')or(f[-4:]=='.tif'))]
MTLFileList = [f for f in dirFileList if (f[-7:]=='MTL.txt')]

#output format (GDAL code)
outFormat = 'KEA'

# run gdal_translate on all TIFs to convert to KEA
for t in tifFileList:
    gdaltranscmd = "gdal_translate -of "+outFormat+" "+t+" "+t[:-4]+".kea"
    print(gdaltranscmd)
    os.system(gdaltranscmd)

# create a new header file referring to .kea files rather than .TIF
for m in MTLFileList:
    with open(m, "r") as inputfile:
        inputtext = inputfile.readlines()
        outputtext = replaceGTIFF_kea(inputtext)
        outputfilebase = m[:-4]
        outputfile = outputfilebase + "_kea.txt"
        out = open(outputfile,"w")
        out.write(outputtext)
        out.close()
