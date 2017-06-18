# run this from within the system envvars
# in the images directory
# this will run first in the system context to do
# extract geotags, resize images and do the shapefile stuff
# and then source the miniconda envvars to do the stuff using rsgislib
import subprocess
import argparse
import sys
# change the below to the path and envvars file
miniconda = '~/.minicondaenvvar'
pathto_script = '~/ioSafeBackup/Python_stuff/bitbucket/rsgislib-landexplorer/readLandCoverGRPs.py'
pathto_resize = '~/ioSafeBackup/Python_stuff/bitbucket/rsgislib-landexplorer/resize_and_convertpng.py'
pathto_pexifscr = '~/ioSafeBackup/Python_stuff/bitbucket/rsgislib-landexplorer/getGPS_folder_pexif.py'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Define the argument for specifying the input file.
    parser.add_argument("-i", "--input", type=str, 
                        help="Specify the input csv file containing points. These are processed into point and bounding box shapefiles, which currently only are generated if a Landsat scene is not specified, which is a workaround because my current conda installation of python doesn't do the shapefiles properly, returning an error at the point of 'from osgeo import ogr'. What I am currently doing is running once with only the file coordinates file specified, on my system python installation, and then again with the Landsat file specified with the conda python installation (which has a working RSGISLib, which my system python installation does not! ")
    parser.add_argument("-s", "--scene", type=str,
                        help="Specify the Landsat scene (currently expects projected to OSGB36, unless the UTM has been specified in the -u parameter).")
    parser.add_argument("-u", "--utm", type=str,
                        help="Specify Universal Transverse Mercator zone, e.g. '30N'. Landsat images of GB are in UTM30N (EPSG:32630), or possibly 29N of 31N.")
    parser.add_argument("--extractgeo", action="store_true",
                        help="optional argument to extract geotags from image files into input file first")
    parser.add_argument("--makepng", action="store_true",
                        help="optional argument to make reduced size pngs from any jpgs in the directory first.")
    parser.add_argument("-a", "--atmoscorr", action="store_true", default=False, help="Specify whether it is an atmospheric corrected in sen2cor within SNAP toolbox Sentinel2 image at 10m resolution with 19 bands (10 image bands). If it is a Level 2 product downloaded from Copernicus in that form and only resampled to 10m, don't use this switch.")
    parser.add_argument("-b8", "--band8Aorder", action="store_true", default=False, help="Specify whether it is a Level 2 product downloaded from Copernicus in that form and only resampled (not atmosphere corrected by the user) to 10m, with band8A between band 8 and 9 rather than at the end (which happened when building stacks previously due to filenames containing B07, B08, B11 , B8A.")

    # Call the parser to parse the arguments.
    args = parser.parse_args()
    # Check that the input parameter has been specified.
    if args.input == None:
        # Print an error message if not and exit.
        print("Error: No input table file provided.")
        sys.exit()
    if args.utm:
        cmd1 = "python {readLpath} -i {coord} -u {utm}".format(coord=args.input, utm=args.utm, readLpath = pathto_script)
        if args.atmoscorr:
            cmd2 = "python {readLpath} -i {coord} -s {scene} -u {utm} -a".format(coord=args.input, scene=args.scene, utm=args.utm, readLpath = pathto_script)
        elif args.band8Aorder:
            cmd2 = "python {readLpath} -i {coord} -s {scene} -u {utm} -b8".format(coord=args.input, scene=args.scene, utm=args.utm, readLpath = pathto_script)
        else:
            cmd2 = "python {readLpath} -i {coord} -s {scene} -u {utm}".format(coord=args.input, scene=args.scene, utm=args.utm, readLpath = pathto_script)
    else:
        cmd1 = "python {readLpath}  -i {coord}".format(coord=args.input)
        if args.atmoscorr:
            cmd2 = "python {readLpath}  -i {coord} -s {scene} -a".format(coord=args.input, scene=args.scene, readLpath = pathto_script)
        elif args.band8Aorder:
            cmd2 = "python {readLpath}  -i {coord} -s {scene} -b8".format(coord=args.input, scene=args.scene, readLpath = pathto_script)
        else:
            cmd2 = "python {readLpath}  -i {coord} -s {scene}".format(coord=args.input, scene=args.scene, readLpath = pathto_script)
    
    if args.extractgeo:
        pexifcmd = "python {pexifc} > {coord}".format(pexifc=pathto_pexifscr, coord = args.input)
        subprocess.call(pexifcmd, shell=True)
    if args.makepng:
        resizecmd = "python {resizepath}".format(resizepath=pathto_resize)
        subprocess.call(resizecmd, shell=True)
        
    subprocess.call(cmd1, shell=True)
    print('source {m}'.format(m=miniconda))
    subprocess.call('source {m}'.format(m=miniconda), shell=True)
    subprocess.call(cmd2,shell=True)

    
