import airsim
import numpy as np
import os
from os import path
import tempfile
import cv2
from datetime import date
import setup_path

def take_picture(client,photo_number):
    #airsim.wait_key('Press any key to take images')
    # responses = client.simGetImages([
    #     airsim.ImageRequest("3", airsim.ImageType.DepthVis),  #depth visualization image
    #     airsim.ImageRequest("3", airsim.ImageType.DepthPerspective, True), #depth in perspective projection
    #     airsim.ImageRequest("3", airsim.ImageType.Scene), #scene vision image in png format
    #     airsim.ImageRequest("3", airsim.ImageType.Scene, False, False)])  #scene vision image in uncompressed RGBA array
    responses = client.simGetImages([airsim.ImageRequest("3", airsim.ImageType.Scene, False, False)])
    response = responses[0]
    print('Retrieved images: %d' % len(responses))

    today = date.today()
    folder = './images_guidance_witten/' + str(today)
    if not path.exists(folder):
        os.mkdir(folder)
    print("Saving images to %s" % folder)

    filename = os.path.join(folder, "photo{}".format(photo_number))

    # get numpy array
    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
    # reshape array to 4 channel image array H X W X 4
    img_rgb = img1d.reshape(response.height, response.width, 3)
    cv2.imwrite(os.path.normpath(filename + '.jpg'), img_rgb) # write to jpg

    # for idx, response in enumerate(responses):

    #     filename = os.path.join(folder, str(idx))

    #     if response.pixels_as_float:
    #         print("Type %d, size %d" % (response.image_type, len(response.image_data_float)))
    #         airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
    #     elif response.compress: #jpg format
    #         print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
    #         airsim.write_file(os.path.normpath(filename + '.jpg'), response.image_data_uint8)
    #     else: #uncompressed array
    #         print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
    #         img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
    #         img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 4 channel image array H X W X 3
    #         cv2.imwrite(os.path.normpath(filename + '.jpg'), img_rgb) # write to jpg