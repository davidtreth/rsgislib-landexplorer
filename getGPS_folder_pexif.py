# get gps tags for all .jpgs or .JPGS in current folder
# uses pexif: https://github.com/bennoleslie/pexif
import os
import subprocess
def run_command(command):
    p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return p.communicate()
cwd = os.getcwd()
files = os.listdir(cwd)
jpgs = [f for f in files if f[-4:].lower()=='.jpg' or f[-5:].lower()=='.jpeg']
#print(jpgs)
print("{j};{lt};{ln}".format(j='Filename',lt='Lat',ln='Lon'))
for j in jpgs:
    cmd = "python /usr/share/doc/python-pexif/examples/getgps.py "+j
    latlon = run_command(cmd)[0]
    lat = latlon.split(",")[0][1:]
    lon = latlon.split(",")[1][1:-2]
    print("{j};{lt};{ln}".format(j=j,lt=lat,ln=lon))
