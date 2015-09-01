from osgeo import ogr
from osgeo import osr
source = osr.SpatialReference()
# assume input data is WGS84 lat,long which it will be for GPS
source.ImportFromEPSG(4326)

def reprojPoint(lat, lon, epsg):
    """ reproject a point to the specified reference epsg """
    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg)
    transform = osr.CoordinateTransformation(source, target)
    point = ogr.CreateGeometryFromWkt("POINT ({x} {y})".format(x=lon,y=lat))
    point.Transform(transform)
    return point

def reproj2FloatPoint(lat,lon, epsg):
    """ take the output of reprojPoint and convert to floating point tuple """
    point = reprojPoint(lat,lon,epsg)
    pWkt = point.ExportToWkt()
    p = pWkt.split('(')[1]
    p = p.split(')')[0]
    x,y = [float(i) for i in p.split(" ")]
    return x,y

def reproj2IntPoint(lat,lon,epsg):
    """ take output of reproj2FloatPoint and return as integer tuple """
    x,y = [int(i) for i in reproj2FloatPoint(lat,lon,epsg)]
    return x,y
    
def printReprojPoint(lat,lon,epsg,roundInt = False):
    """ version of function printing to console - for testing """
    x,y = reproj2FloatPoint(lat,lon,epsg)
    if roundInt:
        print("{east} {north}".format(east=int(x),north=int(y)))
    else:
        print("{east} {north}".format(east=x,north=y))


if __name__ == "__main__":
    printReprojPoint(50.26,-5,27700,True)