import airsim
import setup_path
import numpy as np
import cv2
from time import sleep
import os
import pprint
import takeimage
from set_image_position import set_image_position
from airsimgeo import AirSimGeoClient

folder ='./images_guidance_witten/'
if not os.path.exists(folder):
    os.mkdir(folder)

gps_loc = open("images_guidance_witten/Positions.txt", "w")
gps_loc.write("imageName,latitude,longitude,altitude\n")
photo_number = 0
numberOfPhotos = 12
numberOfPaths = 3
height = -100
SRID = 'EPSG:3857'
ORIGIN = (7.33577, 51.43672, 94)

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client_geo = AirSimGeoClient(srid=SRID, origin=ORIGIN)
home_Geopoint = client.getHomeGeoPoint()
client.confirmConnection()
client.enableApiControl(True)

# Go up by 15 meters
print("Taking off...")
client.armDisarm(True)
client.takeoffAsync().join()
gps_new = (home_Geopoint.longitude, home_Geopoint.latitude, home_Geopoint.altitude + 15.0)
client_geo.moveToPositionAsyncGeo(gps=gps_new, velocity=5).join()

#Path1
pos_ini_x1 = 9
pos_fin_x1 = 160
delta_x1 = pos_fin_x1 - pos_ini_x1
photosPath = int(numberOfPhotos/numberOfPaths)
step1 = delta_x1/(photosPath)
pos_ini_y1 = -15

# Move to Initial position
client.moveToPositionAsync(pos_ini_x1, pos_ini_y1, height, 5).join()
sleep(5)
gps_data = client_geo.getGpsLocation()
s = pprint.pformat(gps_data)
print("\ngps_data: %s\n" % s)
takeimage.take_picture(client, photo_number)
gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

# Moving by path1
for photo_number in range(photosPath - 1):
    photo_number = photo_number + 1
    x = client.simGetVehiclePose().position.x_val
    client.moveToPositionAsync((x + step1), pos_ini_y1, height, 5).join()
    sleep(2)
    print("\nPosition of photo {}".format(photo_number))
    gps_data = client_geo.getGpsLocation()
    s = pprint.pformat(gps_data)
    print("\ngps_data: %s\n" % s)
    takeimage.take_picture(client, (photo_number))
    gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
    set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

# only 1 step
photo_number = photosPath
x = client.simGetVehiclePose().position.x_val
client.moveToPositionAsync(x, -58, height, 5).join()
sleep(5)
gps_data = client_geo.getGpsLocation()
s = pprint.pformat(gps_data)
print("\ngps_data: %s\n" % s)
takeimage.take_picture(client, photo_number)
gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

#Path2
pos_ini_x2 = 160
pos_fin_x2 = 9
delta_x2 = pos_fin_x2 - pos_ini_x2
step2 = delta_x2/(photosPath)
pos_ini_y2 = client.simGetVehiclePose().position.y_val

for photo_number in range(photosPath, (2*photosPath)-1):
    photo_number = photo_number + 1
    x = client.simGetVehiclePose().position.x_val
    client.moveToPositionAsync((x + step2), pos_ini_y2, height, 5).join()
    sleep(2)
    print("\nPosition of photo {}".format(photo_number))
    gps_data = client_geo.getGpsLocation()
    s = pprint.pformat(gps_data)
    print("\ngps_data: %s\n" % s)
    takeimage.take_picture(client, (photo_number))
    gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
    set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

# only 1 step
photo_number = 2*photosPath
x = client.simGetVehiclePose().position.x_val
client.moveToPositionAsync(x, -95 , height, 5).join()
sleep(5)
gps_data = client_geo.getGpsLocation()
s = pprint.pformat(gps_data)
print("\ngps_data: %s\n" % s)
takeimage.take_picture(client, photo_number)
gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

#Path3
pos_ini_x3 = 9
pos_fin_x3 = 160
delta_x3 = pos_fin_x3 - pos_ini_x3
step3 = delta_x3/(photosPath)
pos_ini_y3 = client.simGetVehiclePose().position.y_val

for photo_number in range((2*photosPath), numberOfPhotos-1):
    photo_number = photo_number + 1
    x = client.simGetVehiclePose().position.x_val
    client.moveToPositionAsync((x + step3), pos_ini_y3, height, 5).join()
    sleep(2)
    print("\nPosition of photo {}".format(photo_number))
    gps_data = client_geo.getGpsLocation()
    s = pprint.pformat(gps_data)
    print("\ngps_data: %s\n" % s)
    takeimage.take_picture(client, (photo_number))
    gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number), gps_data[1], gps_data[0], gps_data[2]))
    set_image_position((photo_number), gps_data[1], gps_data[0], gps_data[2])

gps_loc.close()
print("Returning to home...")
client.moveToGPSAsync(home_Geopoint.latitude, home_Geopoint.longitude, 110, 5).join()
client.moveToPositionAsync(0,0, client.simGetVehiclePose().position.z_val + 15, 5)
print("Landing")
client.landAsync().join()
client.armDisarm(False)