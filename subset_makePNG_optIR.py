#import python modules
import rsgislib
import rsgislib.imageutils
import rsgislib.imagecalc
# from rsgislib import zonalstats
# I had some trouble with this so decided to subset to a temporary file
# and then use imagecalc instead
import os
import errno

# the optical + near infrared bands of Landsat data
LS8bands = ['Coastal','Blue','Green','Red','NIR','SWIR1','SWIR2']
LS7bands = ['Blue','Green','Red','NIR','SWIR1','TIR','SWIR2']
tmpdir = 'tmp/'

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        
def makePNG(inputStack,bands=[1,2,3,4,5,6,7],bnames=LS8bands,datatype=rsgislib.TYPE_32FLOAT, format='KEA'):
    """ make PNG files for RGB and SWIR2NIRRed "with 2.5 stddev stretch """
    bandDefns = []    
    for b in range(len(bands)):
         bandDefns.append(rsgislib.imagecalc.BandDefn(bnames[bands[b]-1],inputStack,bands[b]))
    rsgisType_o = rsgislib.TYPE_8INT
    stretchType = rsgislib.imageutils.STRETCH_LINEARSTDDEV
    nsigma = 2.5 #number of std devs for stretch
    # create tmpdir if it doesn't exist yet
    make_sure_path_exists(tmpdir)
    for b in bandDefns:
        # save stretched image in tmpdir
        # 2.5 sigma lin stretch
        tempFile = tmpdir+b.bandName+"_tmp1.kea"
        stretchFile = tmpdir+b.bandName+"_tmpstr.kea"
        statsFile = tmpdir+b.bandName+"_stats.txt"
        rsgislib.imageutils.selectImageBands(inputStack, tempFile,'KEA',
                                             datatype,[b.bandIndex])
        # set saveoutstats=True,ignorezeros=True,onepassd=False 
        rsgislib.imageutils.stretchImage(tempFile, stretchFile, True,
                                         statsFile, True, False, 'KEA',
                                         rsgisType_o, stretchType, nsigma)

    # bands 432 (if LS8)
    outTIFFile = inputStack[:-4] + "_RGB.tif"
    outPNGFile = inputStack[:-4] + "_RGB.png"
    # this is all a bit confusing with the indices, because bands start with 1
    # and arrays start with 0, and the LS7 band 6 is TIR and not expected in the
    # layerstack
    if bnames[0] == 'Blue' or bnames[0] == 'B2Blue':
        # ie if LS7 or processed Sentinel2 image
        # for LS8 it is 'Coastal' and raw Sentinel2 'B1Coastal'
        RGB = [2,1,0]
    else:
        RGB = [3,2,1]
    inputstrfiles= [tmpdir+bnames[RGB[0]]+"_tmpstr.kea",
                    tmpdir+bnames[RGB[1]]+"_tmpstr.kea",
                    tmpdir+bnames[RGB[2]]+"_tmpstr.kea"]
    # temporarily output to GeoTIFF
    rsgislib.imageutils.stackImageBands(inputstrfiles,
                                        [bnames[RGB[0]],bnames[RGB[1]],bnames[RGB[2]]],
                                         outTIFFile, None, 0, 'GTiff', rsgisType_o)
    # use ImageMagick in shell to convert to PNG
    os.system("convert {i} {o}".format(i=outTIFFile,o=outPNGFile))
    os.remove(outTIFFile)
    # bands 754 (LS8)    
    if bnames[0] == 'Blue':
        # ie if LS7 - band 6 (of stack)/band 7 of original data is SWIR2
        # band 4 is NIR, band 3 is Red
        RGB = [5,3,2]
        outTIFFile = inputStack[:-4] + "_743.tif"
        outPNGFile = inputStack[:-4] + "_743.png"
    elif len(bnames) == 13:
        # for Sentinel2 there are 13 bands
        # and band 12 is SWIR2, 8 is broadband NIR, 4 Red
        RGB = [11,7,3]
        outTIFFile = inputStack[:-4] + "_1284.tif"
        outPNGFile = inputStack[:-4] + "_1284.png"
    elif len(bnames) == 10:
        # Sentinel 2 image processed to L2A in SenCor
        # at 10m resolution
        # in the stack
        # 10th band is B12, 7th is B8, 3rd is B4
        RGB = [9, 6, 2]
        outTIFFile = inputStack[:-4] + "_1284.tif"
        outPNGFile = inputStack[:-4] + "_1284.png"
    else:
        # ie if LS8 - this time band 7 is SWIR2, 5 NIR and 4 Red
        RGB = [6,4,3]
        outTIFFile = inputStack[:-4] + "_754.tif"
        outPNGFile = inputStack[:-4] + "_754.png"
    inputstrfiles= [tmpdir+bnames[RGB[0]]+"_tmpstr.kea",
                    tmpdir+bnames[RGB[1]]+"_tmpstr.kea",
                    tmpdir+bnames[RGB[2]]+"_tmpstr.kea"]
    # temporarily output to GeoTIFF
    rsgislib.imageutils.stackImageBands(inputstrfiles,
                                        [bnames[RGB[0]],bnames[RGB[1]],bnames[RGB[2]]],
                                        outTIFFile, None, 0, 'GTiff', rsgisType_o)
    # use ImageMagick in shell to convert to PNG
    os.system("convert {i} {o}".format(i=outTIFFile,o=outPNGFile))
    os.remove(outTIFFile)

def getSpectrum(inputStack, GRPshp):
    """ return band stats for the image inputStack in ground ref shapefile """
    outTXT = GRPshp[:-4]+"_spec.csv"
    rsgislib.imagecalc.imageBandStats(inputStack,outTXT,True)
    #zonalstats.pointValue2TXT(inputStack, GRPshp, outTXT)
