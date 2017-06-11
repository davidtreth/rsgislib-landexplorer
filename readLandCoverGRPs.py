import csv
import sys
# reproject points
import reprojWGS84LatLon2OSGB36 as OSGB
import bboxSHP

# Import the python Argument parser
import argparse
import os
import glob
# import PIL
from PIL import Image
# I used PIL/Pillow to import jpgs directly without converting to png
# however this version assumes the images have been converted to PNG
# in a subdirectory 'png' after I had some problems with Pillow on Python3
# though reading jpgs now works for me in PIL.Image but not in matplotlib.image
import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
import numpy as np
import errno

# rsgislib imports are moved to under if LSscene:
# so that this same script can be run with my system python installation
# which has working shapefile stuff needed by bboxSHP but not rsgislib
# and by conda where rsgislib works but osgeo.ogr fails in bboxSHP!


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def UTMfindEPSG(zonestr):
    """ find epsg code for specified utm zone """
    if not((zonestr[-1].upper() in ['N','S'])and(
    int(zonestr[:-1])-1 in range(60))):
        # if not in form nnN or nnS
        print("{u} not understood as valid UTM zone. Defaulting to UTM30N epsg:32430.".format(u=zonestr))
        return 32430
    else:
        if zonestr[-1].upper() == 'N':
            epsg = 32400 + int(zonestr[:-1])
        else:
            epsg = 32500 + int(zonestr[:-1])
        return epsg

def setTickLabelsLS(ax,gridref, pixelscale=30):
    """ set the tick labels for the preview Landsat images 
    
    this assumes that we are using 3km boxes/ 100 LS pixels"""
    xt = np.arange(0,3500,500)
    ax.set_xticks(xt/pixelscale)
    ax.set_xlim(0,3000/pixelscale)
    ax.set_ylim(3000/pixelscale,0)
    print(xt)
    # tick labels as 6 figure grid refs
    offX = int(gridref[3:6])-pixelscale/2    
    lblx = pixelscale/3000. * xt+ offX
    lblx = np.int16(lblx)
    ax.set_xticklabels(lblx)
    yt = np.arange(0,3500,500)
    print(yt)
    ax.set_yticks(yt/pixelscale)
    offY = int(gridref[6:])-pixelscale/2
    lbly = (3000-yt)*pixelscale/3000. + offY
    lbly = np.int16(lbly)
    ax.set_yticklabels(lbly)
        
def findOSgridref(X,Y,nfig=6):
    """ find lettered 100km grid square and return it
    and grid reference (by default 6 figures) """
    if (X<0)or(Y<0)or(X>1e6)or(Y>15e5):
        print("not in any of the 500km squares in GB")
        return None
    if not(nfig in [2,4,6,8,10]):
        print("nfig should be an even number up to 10. Defaulting to 6 figures.")
        nfig = 6        
    # the 25 letters used as the second letter of grid squares
    letterArr = [['A','B','C','D','E'],
                 ['F','G','H','J','K'],
                 ['L','M','N','O','P'],
                 ['Q','R','S','T','U'],
                 ['V','W','X','Y','Z']]
    # letters used as 1st letter
    # note O is almost entirely sea
    # except a tiny bit of foreshore in
    # Yorkshire and J is all sea
    bigletterArr = [['H','J'],
                   ['N','O'],
                   ['S','T']]        
    # find which big square we are in
    X1, Y1 = int(X/500000), int(Y/500000)
    letter1 = bigletterArr[2-Y1][X1]
    # which 100km x 100km square ?
    X2, Y2 = int((X-X1*500000)/100000), int ((Y-Y1*500000)/100000)
    letter2 = letterArr[4-Y2][X2]
    gridsq = letter1 + letter2
    # coordinates within the square
    denom = 100000/(10**(nfig/2))
    easting, northing = int((X % 100000)/denom), int((Y % 100000)/denom)
    return gridsq, easting, northing

def readGRP(groundRefPointsFile, epsg, LSscene = None, plotsOutPath = "outputplots/", L2A=False):
    """ take the list of ground reference points and their associated image files
    and make some plots """
    # print(epsg)
    with open(groundRefPointsFile) as csvinfile:
        # read the file which contains the filenames of the images, and 
        # GPS coordinates lat, long
        reader = csv.DictReader(csvinfile, delimiter = ';')
        # this project started with some geotagged images some of which had spurious
        # coordinates which needed to be manually edited, whereby the edited coordinates 
        # went in the 'LatCleaned' and 'LonCleaned' columns in the data
        if not((('LatCleaned' in reader.fieldnames) and ('LonCleaned' in reader.fieldnames))
            or(('Lat' in reader.fieldnames) and ('Lon' in reader.fieldnames))):
            print("expecting columns labelled 'LatCleaned' and 'LonCleaned' or 'Lat' and 'Lon'")
            sys.exit()
        fnames = reader.fieldnames    
        # sanity check to make sure the columns are reading in ok
        print(fnames)
    # output plots
    make_sure_path_exists(plotsOutPath)
    # create output plots directory
    # read the data into an array
    rowsdata = []
    with open(groundRefPointsFile) as csvinfile:
        reader = csv.DictReader(csvinfile,delimiter=';')
        for row in reader:            
            rowsdata.append(row)
    #print(rowsdata)   
#    trip, site, fname, json, lat, lon, latCl, lonCl, notes, llOver = [[row[f] for f in fnames] for row in rowsdata]
    fname = []
    lat = []
    lon = []
    for row in rowsdata:
        fname.append(row['Filename'])
        # if the 'Cleaned' columns of manually edited data exist use them otherwise
        # use 'Lat' and 'Lon'
        if not(('LatCleaned' in reader.fieldnames) and ('LonCleaned' in reader.fieldnames)):
            lat.append(float(row['Lat']))
            lon.append(float(row['Lon']))
        else:
            lat.append(float(row['LatCleaned']))
            lon.append(float(row['LonCleaned']))
    llons = zip(lat, lon)
    # reproject to the spatial reference (should be that of the satellite image)
    XYs = [OSGB.reproj2IntPoint(ll[0],ll[1],epsg) for ll in llons]
    #print(XYs)
    # if the satellite image has a different coordinate system to OSGB36
    # create a separate set of coordinates in OSGB for labelling
    if not(epsg==27700):
        llons = zip(lat, lon)
        OSGBxys = [OSGB.reproj2IntPoint(ll[0],ll[1],27700) for ll in llons]
    else:
        OSGBxys = [i for i in XYs]
    #print(XYs)
    #print(OSGBxys)
    #print([i for i in zip(latCl, lonCl, XYs,fname)])
    for lt, ln, xy, OSGBxy, fn in zip(lat, lon, XYs, OSGBxys, fname):
        print(lt,ln, xy, fn)
        gridsq, east ,north = findOSgridref(OSGBxy[0],OSGBxy[1])
        gridref = gridsq + "_" + str(east) + str(north) 
        print(gridref)
        # create bounding box shapefile of side 3km        
        # and spectral sampling shapefile 4x4 px
        shp3km = gridref +".shp"
        shp120m = gridref +"_120m.shp"
        shp40m = gridref +"_40m.shp"
        shpGRP = gridref +"_point.shp"
        if not(LSscene):
        #if True:
            # currently, if a Landsat scene is specified,
            # don't create the shapefiles - assume they already exist
            # a workaround for my problem with from osgeo import ogr on conda
            bboxSHP.createpointSHP(xy[0],xy[1],shpGRP,epsg)
            bboxSHP.createbboxSHP(xy[0],xy[1],3000,shp3km,epsg)
            bboxSHP.createbboxSHP(xy[0],xy[1],120,shp120m,epsg)
            bboxSHP.createbboxSHP(xy[0],xy[1],40,shp40m,epsg)
        if LSscene:
                import rsgislib
                from rsgislib import imageutils
                import subset_makePNG_optIR    
                # subset LS scene to shp3km and shp120m bbox
                gdalformat = 'KEA'
                datatype = rsgislib.TYPE_32FLOAT
                LSout = LSscene.split('/')[-1]
                print(LSout)
                outputImage = gridref+".kea"
                outputImage120m = gridref+"_120m.kea"
                imageutils.subset(LSscene, shp3km, outputImage, gdalformat, datatype)

                pixelscale = 30
                if LSout[:3] == 'S2A' or LSout[:3] == 'S2B':
                    # Sentinel 2A/2B
                    outputImage40m = gridref+"_40m.kea"
                    imageutils.subset(LSscene, shp40m, outputImage40m, gdalformat, datatype)
                    if L2A:
                        # if atmos-corrected stack produced in sencor
                        S2bands = ['B2Blue', 'B3Green', 'B4Red', 'B5NIR705', 'B6NIR740', 'B7NIR783',
                                    'B8NIR842', 'B8A865nm', 'B11SWIR1610', 'B12SWIR2190']
                        S2bi = [1,2,3,4,5,6, 7, 8,9, 10]
                        wv = [490, 560, 665, 705, 740, 783, 842, 865, 1610, 2190]
                        wv_w = [65, 35, 30, 15, 15, 20, 115, 20, 90, 180]
                        pixelscale = 10
                    else:
                        S2bands = ['B1Coastal', 'B2Blue', 'B3Green', 'B4Red', 'B5NIR705', 'B6NIR740', 'B7NIR783',
                                   'B8NIR842', 'B9WaterVap945', 'B10Cirrus1375', 'B11SWIR1610', 'B12SWIR2190', 'B8A865nm']
                        S2bi = [1,2,3,4,5,6,7,8, 13, 9,10,11,12]
                        wv = [443, 490, 560, 665, 705, 740, 783, 842, 865, 940, 1375, 1610, 2190]
                        wv_w = [20, 65, 35, 30, 15, 15, 20, 115, 20, 20, 30, 90, 180]
                        pixelscale = 10
                    subset_makePNG_optIR.makePNG(outputImage, S2bi, S2bands)
                    subset_makePNG_optIR.getSpectrum(outputImage40m, shpGRP)
                    IR_PNG = outputImage[:-4]+'_1284.png'

                elif LSout[:3] == 'LS7' or LSout[:3] == 'LS5':
                    # if this is Landsat 7 or 5
                    imageutils.subset(LSscene, shp120m, outputImage120m, gdalformat, datatype)
                    LS7bands = ['Blue','Green','Red','NIR','SWIR1','TIR','SWIR2']
                    LS7bi = [1,2,3,4,5,6]
                    wv = [482,563,655,865,1610,2200]
                    subset_makePNG_optIR.makePNG(outputImage,LS7bi,LS7bands)
                    subset_makePNG_optIR.getSpectrum(outputImage120m, shpGRP)
                    IR_PNG = outputImage[:-4]+'_743.png'
                elif LSout[:3] == 'LS8':
                    imageutils.subset(LSscene, shp120m, outputImage120m, gdalformat, datatype)
                    wv = [443,482,563,655,865,1610,2200]
                    subset_makePNG_optIR.makePNG(outputImage)
                    subset_makePNG_optIR.getSpectrum(outputImage120m, shpGRP)
                    IR_PNG = outputImage[:-4]+'_754.png'
                else:
                    print("image {l} not Sentinel2, Landsat 5/7 or Landsat 8".format(l=LSout))
                # the output file of subset_makePNG_optIR.getSpectrum()
                # should probably rewrite to remove possibility of error here
                specFile = shpGRP[:-4]+"_spec.csv"
                print(specFile)
                # read in mean/stddevs for plotting
                means = []
                stddevs = []                        
                with open(specFile) as csvfile:
                    reader = csv.DictReader(csvfile)
                    for r in reader:
                        means.append(float(r['Mean']))
                        stddevs.append(float(r['StdDev']))
                #print(means, stddevs)
                means = np.array(means)
                stddevs = np.array(stddevs)
                # truncate to avoid thematic layers etc. in L2A product for Sentinel2
                means = means[:len(S2bands)]
                stddevs = stddevs[:len(S2bands)]
                # output file of subset_makePNG_optIR.makePNG()
                optPNG = outputImage[:-4]+'_RGB.png'                              
        plottitle = str(lt)+" , "+ str(ln) + " " + gridref.replace("_"," ")
        # assume files are converted to PNG in sub-folder png/
        pngfn = glob.glob("[pP][nN][gG]/"+fn[:-4]+".[pP][nN][gG]")[0]
        #img=mpimg.imread(pngfn)
        img=Image.open(pngfn)
        #img=Image.open(fn)
        img.convert(mode='RGB')
        imgArr = np.asarray(img)                
        #if using PIL can read jpgs directly
        #img=mpimg.imread(fn)        
        #imgR, imgG, imgB = img[:,:,0], img[:,:,1], img[:,:,2]
        imgR, imgG, imgB = imgArr[:,:,0], imgArr[:,:,1], imgArr[:,:,2]
        #print(img)
        print(imgArr.shape)
        #if img.shape[0]> img.shape[1]:
        dimens = [18,12]
        #else:
        #dimens = [16,12]
        fig = plt.figure(num=plottitle,figsize=dimens,facecolor='white')
        fig.set_tight_layout(True)
        ax = plt.subplot(241)
        ax.set_xticks([])
        ax.set_yticks([])
        imgplot = ax.imshow(img)
        ax.set_title(gridref)
        ax = plt.subplot(244)
        ax.set_xticks([])
        ax.set_yticks([])
        imgplot = ax.imshow(imgR, cmap=plt.get_cmap('Reds'))
        #plottitleR = plottitle + " Red"
        ax.set_title("Red")
        #plt.colorbar()
        ax = plt.subplot(243)
        ax.set_xticks([])
        ax.set_yticks([])
        imgplot = ax.imshow(imgG, cmap=plt.get_cmap('Greens'))
        #plottitleG = plottitle + " Green"
        ax.set_title("Green")
        #plt.title(plottitleG)
        #plt.colorbar()
        ax = plt.subplot(242)
        ax.set_xticks([])
        ax.set_yticks([])
        imgplot = ax.imshow(imgB, cmap=plt.get_cmap('Blues'))
        #plottitleB = plottitle + " Blue"
        ax.set_title("Blue")
        #plt.title(plottitleB)
        #plt.colorbar()
        # plot for spectrum of ground ref image
        BGR = np.array([imgB.mean(), imgG.mean(), imgR.mean()])
        BGRstddev = np.array([imgB.std(), imgG.std(), imgR.std()])
        # approximation to wavelength response
        wavelength = np.array([450,550,625])
        ax = plt.subplot(245)
        ax.cla()
        ax.plot(wavelength,BGR,'ko-')
        ax.plot(wavelength,BGR+BGRstddev,'k--',lw=0.2)
        ax.plot(wavelength,BGR-BGRstddev,'k--',lw=0.2)        
        ax.fill_between(wavelength,BGR+BGRstddev,BGR-BGRstddev,color='yellow',alpha=0.25,interpolate=True)
        ax.set_xlim(350,750)
        ax.set_title('Band means of ground image')
        ax.set_xlabel('wavelength (nm)')
        ax.set_ylabel('mean DN')
        if LSscene:
            # if we are using a LS scene, do the plots of that
            # visible light band combination
            optImg = Image.open(optPNG)
            optImg.convert(mode='RGB')
            optImg = np.asarray(optImg)            
            # optImg = mpimg.imread(optPNG)
            ax = plt.subplot(246)
            if pixelscale == 10:
                ax.set_title('RGB Sentinel2 image\n{fn}'.format(fn=LSout[:19]))
            else:
                ax.set_title('RGB Landsat image\n{fn}'.format(fn=LSout[:12]))
            
            imgplot = ax.imshow(optImg)
            setTickLabelsLS(ax,gridref, pixelscale)
            ax.plot([1500/pixelscale],[1500/pixelscale],color='yellow',alpha=1,marker='+',ms=1)
            ax.plot([(1500-2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale],
                    [(1500-2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale], color='white')

            #ax.plot([1440/pixelscale,1440/pixelscale,1560/pixelscale,1560/pixelscale,1440/pixelscale],[1440/pixelscale,1560/pixelscale,1560/pixelscale,1440/pixelscale,1440/pixelscale],color='white')
                
                
            # SWIR2, NIR and Red band combination
            #IR_Img = mpimg.imread(IR_PNG)
            IR_Img = Image.open(IR_PNG)
            IR_Img.convert(mode='RGB')
            IR_Img = np.asarray(IR_Img)
            ax = plt.subplot(247)
            if pixelscale == 10:
                ax.set_title('Bands 12/8/4 Sentinel2 image\n{fn}'.format(fn=LSout[:19]))
            else:
                ax.set_title('Bands 754/743 Landsat image\n{fn}'.format(fn=LSout[:12]))
            imgplot = ax.imshow(IR_Img)
            setTickLabelsLS(ax,gridref, pixelscale)
            ax.plot([1500/pixelscale],[1500/pixelscale],color='yellow',alpha=1,marker='+',ms=1)
            ax.plot([(1500-2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale],
                    [(1500-2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500+2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale,
                     (1500-2*pixelscale)/pixelscale], color='white')
            
            #ax.plot([1440/pixelscale,1440/pixelscale,1560/pixelscale,1560/pixelscale,1440/pixelscale],[1440/pixelscale,1560/pixelscale,1560/pixelscale,1440/pixelscale,1440/pixelscale],color='white')
            ax = plt.subplot(248)
            if pixelscale == 10:
                ax.set_title('Spectrum of Sentinel2 image\nin 40m box around GRP')
            else:
                ax.set_title('Spectrum of Landsat image\nin 120m box around GRP')
            ax.set_xlabel('wavelength (nm)')
            ax.set_ylabel('mean DN')
            ax.set_xticks([500,1000,1500,2000])
            ax.plot(wv,means,'ko-')
            ax.plot(wv,means+stddevs,'k--',lw=0.2)
            ax.plot(wv,means-stddevs,'k--',lw=0.2)
            ax.fill_between(wv,means+stddevs, means-stddevs,color='yellow',alpha=0.25,interpolate=True)
            # output file
            plotsOutFn = plotsOutPath+fn[:-4]+'_'+gridref+'.png'
            plt.savefig(plotsOutFn, bbox_inches='tight')           
            #plt.show()

        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Define the argument for specifying the input file.
    parser.add_argument("-i", "--input", type=str, 
                        help="Specify the input csv file containing points. These are processed into point and bounding box shapefiles, which currently only are generated if a Landsat scene is not specified, which is a workaround because my current conda installation of python doesn't do the shapefiles properly, returning an error at the point of 'from osgeo import ogr'. What I am currently doing is running once with only the file coordinates file specified, on my system python installation, and then again with the Landsat file specified with the conda python installation (which has a working RSGISLib, which my system python installation does not! ")
    parser.add_argument("-s", "--scene", type=str,
                        help="Specify the Landsat scene (currently expects projected to OSGB36, unless the UTM has been specified in the -u parameter).")
    parser.add_argument("-u", "--utm", type=str,
                        help="Specify Universal Transverse Mercator zone, e.g. '30N'. Landsat images of GB are in UTM30N (EPSG:32630), or possibly 29N of 31N.")
    parser.add_argument("-a", "--atmoscorr", action="store_true", default=False, help="Specify whether it is an atmospheric corrected Sentinel2 image at 10m resolution with 19 bands (10 image bands).")
    # Call the parser to parse the arguments.
    args = parser.parse_args()
    # Check that the input parameter has been specified.
    if args.input == None:
        # Print an error message if not and exit.
        print("Error: No input table file provided.")
        sys.exit()
    if args.utm:        
        epsg = UTMfindEPSG(args.utm)
    else:
        epsg = 27700
    # groundRefPointsFile = 'landcover_fieldtrips_groundrefpoints.csv'
    # expect the csv file of locations,
    # with the headers expected to be:
    # Trip;Site;Filename;Label from JSON;Lat;Lon;LatCleaned;LonCleaned;notes;coordOverride
    # at minimum Filename; Lat; Lon
    groundRefPointsFile = args.input

    if args.scene == None:
        readGRP(groundRefPointsFile,epsg)
    else:
        LandsatScene = args.scene
        readGRP(groundRefPointsFile, epsg, LandsatScene, L2A=args.atmoscorr)
