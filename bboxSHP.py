from osgeo import ogr, osr
import os
def createpointSHP(Xc, Yc,outFile,sref=27700):
    """ takes a lat,long point Xc, Yc and converts to projected coords
    by default OSGB36 (epsg:27700) and saves in a shapefile """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outFile):        
        driver.DeleteDataSource(outFile)
    outDataSource = driver.CreateDataSource(outFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(sref)
    layer = outDataSource.CreateLayer(outFile[:-4],srs, geom_type=ogr.wkbPoint)
    idField = ogr.FieldDefn("id",ogr.OFTInteger)
    layer.CreateField(idField)
    feature = ogr.Feature(layer.GetLayerDefn())
    # create the WKT for the feature using Python string formatting
    wkt = "POINT({x} {y})".format(x=float(Xc) , y=float(Yc))
    # Create the point from the Well Known Txt
    point = ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(point)
    layer.CreateFeature(feature)
    feature.Destroy()
    outDataSource.Destroy()

    
def createbboxSHP(Xc, Yc, side,outFile,sref=27700):
    """ takes a lat,long point Xc, Yc and makes a square around it 
    of length 'side' in projected coords
    by default OSGB36 (epsg:27700) and saves in a shapefile """
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outFile):        
        driver.DeleteDataSource(outFile)    
    outDataSource = driver.CreateDataSource(outFile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(sref)
    layer = outDataSource.CreateLayer(outFile[:-4],srs, geom_type=ogr.wkbPolygon)
    idField = ogr.FieldDefn("id",ogr.OFTInteger)
    layer.CreateField(idField)    
    h = side/2
    # the corner locations of the box
    bboxpoints = [(Xc-h,Yc-h),(Xc-h,Yc+h),(Xc+h,Yc+h),(Xc+h,Yc-h)]
    bboxline = ogr.Geometry(ogr.wkbLinearRing)
    for i in bboxpoints:
        bboxline.AddPoint(i[0],i[1])
    bbox = ogr.Geometry(ogr.wkbPolygon)
    bbox.AddGeometry(bboxline)    
    featureDefn = layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(bbox)
    feature.SetField("id",1)
    layer.CreateFeature(feature)
    outDataSource.Destroy()

