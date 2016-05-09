# create a subdirectory and convert all jpg files to 400pixel wide pngs
import os
from PIL import Image

path = os.getcwd()
filelist = os.listdir(path)
jpgfiles = [f for f in filelist if f[-4:].lower() == ".jpg" or f[-5:].lower() == ".jpeg"]

outsize = 400
outpath = os.path.join(path, 'png')
try:
    os.mkdir(outpath)
except:
    # if it already exists
    pass

for j in jpgfiles:
    img = Image.open(os.path.join(path,j))
    img = img.convert('RGB')
    width, height = img.size
    outheight = int((float(outsize)/width) * height)
    outfile = j.split(".")[0] + '.png'
    if width > outsize:
        out = img.resize((outsize, outheight))
    else:
        out = img
    out.save(os.path.join(outpath,outfile), "png")
