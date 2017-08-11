__author__ = 'Christoph Graf'

# Name: convert_and_append.py
# Description: quick and dirty conversion of the type of some properties,
#              adding the visitor_id as property and
#              appending it all to one result shapefile
#
# Version 1 - 5.11.2014
# Usage: python convert_append.py (ArcGIS arcpy library has to be present)

# import system modules
import arcpy, os, locale
from arcpy import env

# set environment
env.workspace = "E:\TATRA\INPUT"
outLocation = "E:\TATRA\OUTPUT"
emptyFC = "EMPTYMASTER.shp"
schemaType = "NO_TEST"
fieldMappings = ""
subtype = ""

codeblock_double = """def checkINF(param):
    if not param == "INF":
        return locale.atof(param)
    else:
        return 999999
 """
codeblock_int = """def checkMinus(param):
    if not param == "-":
        return sint(param)
    else:
        return 999999
 """

# define a helper function to check if a certain fieldname exists in a list of fields
def field_exits(fields, field):
  for f in fields:
    if f.name == field:
        return True
  return False

def ignore_exception(IgnoreException=Exception,DefaultVal=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal
        return _dec
    return dec
sint = ignore_exception(ValueError)(int)

try:
    # create a new empty result shapefile
    if arcpy.Exists(outLocation + "\RESULT.shp"):
        arcpy.Delete_management(outLocation + "\RESULT.shp")
    #arcpy.CreateFeatureclass_management(outLocation, "RESULT.shp", "POINT", emptyFC)
    arcpy.Copy_management(emptyFC, outLocation + os.sep + "RESULT.shp")


    # get all point shapefiles in the input directory as input list
    inputList = arcpy.ListFeatureClasses("","POINT")

    # process every file in list
    for myfc in inputList:

        # skip the empty master
        if myfc == "EMPTYMASTER.shp":
            continue

        print "Processing: " + myfc
        vid = int(myfc.split(".")[0].split("_")[-1])

        # add new fields if they don't exist and fill the new fields with the calculated data
        fields = arcpy.ListFields(myfc)
        if not field_exits(fields, "date"):
            arcpy.AddField_management(myfc, "date", "TEXT")
        arcpy.CalculateField_management(myfc, "date", "str(!Day_!).zfill(2) + '.' + str(!Month_!).zfill(2) + '.' + str(!Year!).zfill(2)", "PYTHON")
        if not field_exits(fields, "time"):
            arcpy.AddField_management(myfc, "time", "TEXT")
        arcpy.CalculateField_management(myfc, "time", "str(!Hour!).zfill(2) + ':' + str(!Min!).zfill(2) + ':' + str(!Sec!).zfill(2)", "PYTHON")
        if not field_exits(fields, "TP_num"):
            arcpy.AddField_management(myfc, "TP_num", "LONG")
        arcpy.CalculateField_management(myfc, "TP_num", "checkMinus(!TP!)", "PYTHON", codeblock_int)
        if not field_exits(fields, "VP_num"):
            arcpy.AddField_management(myfc, "VP_num", "DOUBLE")
        arcpy.CalculateField_management(myfc, "VP_num", "checkINF(!VP__km_hr_!)", "PYTHON", codeblock_double)
        if not field_exits(fields, "VID"):
            arcpy.AddField_management(myfc, "VID", "LONG")
        arcpy.CalculateField_management(myfc, "VID", vid)



    # append to the result file
    # arcpy.Append_management(inputList, outLocation + os.sep + "RESULT.shp", schemaType, fieldMappings, subtype)

except Exception as e:
    print e.message
