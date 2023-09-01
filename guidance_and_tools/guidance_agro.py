import airsim
import setup_path
import numpy as np
import cv2
from time import sleep
import os
import pprint
import takeimage
from set_image_position import set_image_position

# waypoints = [[-3.7018564,-47.7648301],[-3.7018424,-47.7649566],[-3.7018284,-47.7650877]]
# client.moveToGPSAsync(-3.7018564, -47.7648301, 146, 5).join()
# client.moveToGPSAsync(-3.7018424, -47.7649566, 146, 5).join()
# client.moveToGPSAsync(-3.70180371, -47.76494038, 142, 5).join()
# client.moveToGPSAsync( -3.70182358, -47.76493493, 142, 5).join()

folder ='./images_guidance/'
if not os.path.exists(folder):
    os.mkdir(folder)

gps_loc = open("images_guidance/Positions.txt", "w")
gps_loc.write("imageName,latitude,longitude,altitude\n")
photo_number = 0
numberOfPhotos = 8

height = -10
pos_ini_y = -25
pos_fin_y = 25
delta_y = pos_fin_y - pos_ini_y
step = delta_y/numberOfPhotos
pos_ini_x = 8

# connect to the AirSim simulator
client = airsim.MultirotorClient()
home_Geopoint = client.getHomeGeoPoint()
client.confirmConnection()
client.enableApiControl(True)
client.moveToPositionAsync(-25,10,client.simGetVehiclePose().position.z_val, 8).join()

alt = client.simGetVehiclePose().position.z_val
# client.getMultirotorState().kinematics_estimated.orientation

print("Taking off...")
client.armDisarm(True)
client.takeoffAsync().join()

print("Moving...")
client.moveToPositionAsync(pos_ini_x,pos_ini_y,height, 2).join() #Initial position to start take pictures
sleep(2)
print("\nPosition of photo {}".format(photo_number))
gps_data = client.getGpsData().gnss.geo_point
s = pprint.pformat(gps_data)
print("\ngps_data: %s\n" % s)
sleep(3)
takeimage.take_picture(client, photo_number)
gps_loc.write("photo%d,%s,%s,%s\n" %(photo_number,gps_data.latitude,gps_data.longitude,gps_data.altitude))
set_image_position(photo_number,gps_data.latitude,gps_data.longitude,gps_data.altitude)

for photo_number in range(numberOfPhotos-1):
    photo_number = photo_number + 1
    y = client.simGetVehiclePose().position.y_val
    client.moveToPositionAsync(pos_ini_x,(y + step),height, 2).join()
    sleep(3)
    print("\nPosition of photo {}".format(photo_number))
    gps_data = client.getGpsData().gnss.geo_point
    s = pprint.pformat(gps_data)
    print("\ngps_data: %s\n" % s)
    sleep(3)
    takeimage.take_picture(client, (photo_number))
    gps_loc.write("photo%d,%s,%s,%s\n" %((photo_number),gps_data.latitude,gps_data.longitude,gps_data.altitude))
    set_image_position((photo_number),gps_data.latitude,gps_data.longitude,gps_data.altitude)    

gps_loc.close()
print("Returning to home...")
client.moveToGPSAsync(home_Geopoint.latitude, home_Geopoint.longitude, 135, 3).join()
print("Landing")
client.landAsync().join()
client.armDisarm(False)
# client.moveToGPSAsync(51.43735, 7.33709, 115, 3)