from flask import Flask, render_template_string, Response

import airsim
import cv2
import numpy as np

client = airsim.MultirotorClient()
client.confirmConnection()

CAMERA_NAME = '3'

#Receive here a flag resolution via zmq 
frame_size = 3
if frame_size == 5:
    pass
elif frame_size == 0:
    scale_resolution = (426,240)
elif frame_size == 1:
    scale_resolution = (640,360)
elif frame_size == 2:
    scale_resolution = (854,480)
elif frame_size == 3:
    scale_resolution = (1280,720)
elif frame_size == 4:
    scale_resolution = (1920,1080)
# else:
#     scale_resolution = (2560,1440) # It is the default resolution in settings.json

IMAGE_TYPE = airsim.ImageType.Scene
DECODE_EXTENSION = '.jpg'

def frame_generator():
    while (True):
        response_image = client.simGetImage(camera_name=CAMERA_NAME, image_type=IMAGE_TYPE, vehicle_name="D1")
        np_response_image = np.asarray(bytearray(response_image), dtype="uint8")
        decoded_frame = cv2.imdecode(np_response_image, cv2.IMREAD_COLOR)
        if frame_size != 5:
            decoded_frame = cv2.resize(decoded_frame, dsize=scale_resolution, interpolation=cv2.INTER_LINEAR) #resize image
        ret, encoded_jpeg = cv2.imencode(DECODE_EXTENSION, decoded_frame)
        frame = encoded_jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

app = Flask(__name__) #instancia

@app.route('/') #Caminho - homepage
# O que será exibido
def index():
    return render_template_string(
        """
            <html>
            <head>
                <title>AirSim Streamer</title>
            </head>
            <body>
                <h1>AirSim Streamer</h1>
                <hr />
                Please use the following link: <a href="/video_feed">http://localhost:5000/video_feed</a>
            </body>
            </html>
        """
        )

@app.route('/video_feed')
def video_feed():
    return Response(
            frame_generator(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
