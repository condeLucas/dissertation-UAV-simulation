import piexif
from PIL import Image
import os
import pandas as pd
from datetime import date

def set_image_position(photo_number, latitude, longitude, altitude):
    # Open source path and destination path
    today = date.today()
    originPath = "./images_guidance_witten/" + str(today)
    destPath = "./images_guidance_witten/" + str(today) + "/geo_images/"
    if not os.path.exists(destPath):
        os.mkdir(destPath)
    print("Saving images to %s" % destPath)

    # Open position data as pandas dataframe
    # gpsPos = pd.read_csv("./images/Positions.txt",index_col=0)
    # gpsPos.head()

    def convertLat(lat):
        if lat > 0:
            latMarker = b'N'
        else: 
            latMarker = b'S'

        lat = abs(lat)
        degress = int(lat)

        tempMinutes = (lat % 1)*60
        minutes = int(tempMinutes)

        tempSeconds = (tempMinutes % 1)*60   
        seconds = int(tempSeconds * 10000)

        latTuple = ((degress, 1), (minutes, 1), (seconds, 10000))
        return latMarker, latTuple

    def convertLon(lon):
        if lon > 0:
            lonMarker = b'E'
        else: 
            lonMarker = b'W'

        lon = abs(lon)
        degress = int(lon)

        tempMinutes = (lon % 1)*60
        minutes = int(tempMinutes)

        tempSeconds = (tempMinutes % 1)*60   
        seconds = int(tempSeconds * 10000)

        lonTuple = ((degress, 1), (minutes, 1), (seconds, 10000))

        return lonMarker, lonTuple

    #for index, row in gpsPos.iterrows():
        #working with the exif data
    exifDict = {'GPS':
                {0: (2, 4, 0, 0),
                5: 0}
            }
    latMarker, latTuple = convertLat(latitude)
    lonMarker, lonTuple = convertLon(longitude)
    exifDict['GPS'][1] = latMarker
    exifDict['GPS'][2] = latTuple
    exifDict['GPS'][3] = lonMarker
    exifDict['GPS'][4] = lonTuple
    exifDict['GPS'][6] = (int(altitude*1000),1000)
    #working with the file
    #opening the original file
    origName=os.path.join(originPath,"photo"+str(photo_number)+".jpg")
    img=Image.open(origName)
    #write the destination file
    destName=os.path.join(destPath,"photo"+str(photo_number)+".jpg")
    exifBytes = piexif.dump(exifDict)
    img.save(destName, exif=exifBytes)