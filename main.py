# https://tutorial.cytron.io/2020/06/12/face-detection-on-pi-camera-image-using-opencv-python3-on-raspberry-pi/

import numpy as np
import cv2 as cv
import io
import picamera

stream = io.BytesIO()

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.capture(stream, format = 'jpeg')


buff = np.frombuffer(stream.getvalue(), dtype = np.uint8)

