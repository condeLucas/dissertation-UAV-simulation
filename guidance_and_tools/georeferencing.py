# This algorithm is based on the paper: Correia, Carlos AM, et al. "Comprehensive Direct Georeferencing of Aerial Images for Unmanned Aerial Systems Applications." Sensors 22.2 (2022): 604.

from cv2 import transpose
import numpy as np
import navpy as nav
import math 
from pyproj import Proj

# This application procedes the automatic georeferencing of an image pixel point in the navigation frame, or in the ENU Frame
def georef(u, v, latitude, longitude, altitude, zENU):

    # myProj = Proj("+proj=utm +zone=23 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    # UTM_x, UTM_y = myProj(longitude, latitude)
    UTM_x = longitude 
    UTM_y = latitude

    ## 1st step: rotation from Image to Camera frames

    #Input the camera intrinsic parameters
    f = 12
    FOV = 90
    ImageWidth = 2048
    SensorWidth = np.tan(np.radians(FOV/2))*2*f
    # SensorWidth = 8.6
    ImageHeight = 1024 
    SensorHeight = 8

    # Based on these parameters we can calculate the FOV and set in Airsim settings.json
    # FOV = np.degrees(2*np.arctan(SensorWidth/(2*f)))
    # If we already have FOV we can find another parameter like:
    # SensorWidth = np.tan(np.radians(FOV/2))*2*f
    fx = f*(ImageWidth/SensorWidth)
    cx = ImageWidth/2
    fy = f*(ImageHeight/SensorHeight)
    cy = ImageHeight/2
    K = np.array([[fx,0,cx],[0,fy,cy],[0,0,1]])

    # Obtaining the pixel coordinates in the camera frame, "Pc", from the pixel coordinates in the image frame, "Pi"
    # Pixel coordinates
    # u=1353
    # v=459
    #Pixel position matrix in the image frame, "Pi"
    Pi = np.array([u,v,1])
    Pi = Pi.T
    #Pixel position matrix in the camera frame, "PpimeC"
    PprimeC = np.linalg.inv(K)@Pi

    ## 2nd step: rotation from the camera frame to the gimbal frame

    #Rotation matrix from the camera frame to the gimbal frame (is a default, most commonly used)
    Rcg = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    #Rcg = np.array([[1, 0, 1], [1, -1, 0], [0, 1, 0]])
    # translation matrix Tcg between the camera and gimbal positions
    Tcgx = 0
    Tcgy = 0
    Tcgz = 0
    Tcg = np.array([Tcgx, Tcgy, Tcgz])
    Tcg = Tcg.T
    # The prime pixel position in the gimbal frame, PprimeG
    PprimeG = Rcg@PprimeC + Tcg

    # 3rd STEP: rotation from the gimbal frame to the UAS frame 
    
    # Obtaining the Direction Cosine Matrix, Ruasg for matrix rotation from the UAS frame to the Gimbal frame, beacuse the Euler angles are given in relation to the UAS frame
    yawuasg = 0
    pitchuasg = -90
    rolluasg = 0
    # Obtaining the DCM matrix
    Ruasg = nav.angle2dcm(yawuasg,pitchuasg,rolluasg,'deg')
    Rguas = Ruasg.T
    # translation matrix Tguas between the gimbal and UAS frame positions
    Tguasx = 0
    Tguasy = 0
    Tguasz = 0
    Tguas = np.array([Tguasx, Tguasy, Tguasz])
    Tguas = Tguas.T
    PprimeUAS = Rguas@PprimeG + Tguas

    # 4th STEP: coordinates transformation from the UAS frame to the NED frame

    # Obtaining the Direction Cosine Matrix, Ruasned for matrix rotation from the UAS frame to the NED frame
    yawneduas = 0
    pitchneduas = 0
    rollneduas = 0
    # Obtaining the DCM matrix
    Rneduas = nav.angle2dcm(yawneduas,pitchneduas,rollneduas,'deg')
    Ruasned = Rneduas.T
    # translation matrix Tuasned between the UAS and NED positions
    Tuasnedx = 0
    Tuasnedy = 0
    Tuasnedz = 0
    Tuasned = np.array([Tuasnedx, Tuasnedy, Tuasnedz])
    #pixel position in the NED frame
    PprimeNED = Ruasned@PprimeUAS + Tuasned
    
    # 5th STEP: coordinates transformation from the NED frame to the ENU frame

    # Rotation matrix from the NED frame to the ENU frame 
    Rnedenu = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    # translation matrix Tnedenu between the NED and ENU positions
    Tnedenu = np.array([UTM_x, UTM_y, altitude])
    # The prime pixel position in the ENU frame, PprimeENU
    PprimeENU = Rnedenu@PprimeNED + Tnedenu
    #print(PprimeENU)

    # 6th STEP: determination of the real pixel coordinates in the ENU frame

    # Following the precedent equations, the complete translation matrix will be given by:
        #Tall = Rnedenu*Ruasned*Rguas*Tcg+Rnedenu*Ruasned*Tguas+Rnedenu*Tuasned+Tnedenu
    Tall = Rnedenu@Ruasned@Rguas@Tcg + Rnedenu@Ruasned@Tguas + Rnedenu@Tuasned + Tnedenu
    # In order to determine the xENU and uENU, the zC factor must be determined
    zTall = Tall[2]
    zPprimeENU = PprimeENU[2]
    zC = (zENU-zTall)/(zPprimeENU-zTall)
    xENU = zC*PprimeENU[0]-zC*Tall[0]+Tall[0]
    yENU = zC*PprimeENU[1]-zC*Tall[1]+Tall[1]

    P_ENU = np.array([xENU, yENU, zENU])

    lon, lat = myProj(xENU, yENU, inverse=True)
    # print(lon)
    # print(lat)
    pixel_georef = np.array([lat, lon])

    print(P_ENU)

    return pixel_georef

if __name__ == '__main__':
    u=1442 #x_center of the detected bounding box
    v=210  #y_center of the detected bounding box

    gps = [51.437362612509006, 7.337106613531333, 112.56271171569824] # Drone coordinate = [latitude, longitude, altitude]
    zENU = 109.56271171569824 # Altitude of the object of interest

    # Convert GPS (decimal degrees) to UTM
    myProj = Proj("+proj=utm +zone=32 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    UTM_x, UTM_y = myProj(gps[1], gps[0]) # myProj(longitude, latitude) --> x = longitude; y = latitude

    pixel_georef = georef(u, v, UTM_y, UTM_x, gps[2], zENU)
    print(pixel_georef)
    