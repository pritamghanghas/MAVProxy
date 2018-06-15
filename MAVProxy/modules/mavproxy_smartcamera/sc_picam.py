"""
sc_picam.py

This file includes functions to:
    call a deamon named pimjpegserver.py running on local
    host to save current image with geotags
"""

import sys
import time
import math
import sc_config
import os
import cv2
from requests_futures.sessions import FuturesSession

class PiCam:
    def __init__(self, instance):

        # health
        self.healthy = False;

        # record instance
        self.instance = instance
        self.config_group = "camera%d" % self.instance
        self.camera_name = 'PiCam'

        self.media_dir = os.path.expanduser(sc_config.config.get_string('general', 'media_dir', '~/media'))
        self.photos_dir = os.path.join(self.media_dir, self.camera_name, 'photos')
        self.video_dir = os.path.join(self.media_dir, self.camera_name, 'videos')

        print (self.photos_dir)

        self.vehicleLat = 0.0              # Current Vehicle Latitude
        self.vehicleLon = 0.0              # Current Vehicle Longitude
        self.vehicleHdg = 0.0              # Current Vehicle Heading
        self.vehicleAMSL = 0.0             # Current Vehicle Altitude above mean sea level

        # background image processing variables
        self.img_counter = 0        # num images requested so far

        # latest image captured
        self.latest_image = None

        self.session = FuturesSession()

    # __str__ - print position vector as string
    def __str__(self):
        return "SmartCameraWebCam Object "

    def boSet_GPS(self, mGPSMessage):
        if mGPSMessage.get_type() == 'GLOBAL_POSITION_INT':
            (self.vehicleLat, self.vehicleLon, self.vehicleHdg, self.vehicleAMSL) = (mGPSMessage.lat*1.0e-7, mGPSMessage.lon*1.0e-7, mGPSMessage.hdg*0.01, mGPSMessage.alt*0.001)

    # latest_image - returns latest image captured and write it to file
    def get_latest_image(self):
        session_dir = os.path.join(self.photos_dir, str(self.instance))
        imgfilename = "img-%d.jpg" % (self.get_image_counter())
        complete_filename = os.path.join(session_dir,imgfilename)
        self.session.get('http://127.0.0.1:5555/capture?filename=%s&lat=%.10f&lon=%.10f&alt=%.10f' % (complete_filename,self.vehicleLat, self.vehicleLon, self.vehicleAMSL))
        return self.latest_image

    # get_image_counter - returns number of images captured since startup
    def get_image_counter(self):
        return self.img_counter

    # take_picture - take a picture
    #   returns True on success
    def take_picture(self):
        # setup video capture
        print("Taking Picture")
        self.img_counter = self.img_counter+1
        self.get_latest_image()
        return True

    # main - tests SmartCameraWebCam class
    def main(self):

        while True:
            try:
                # send request to image capture for image
                if self.take_picture():
                    # display image
                    print("took one picture")
                    # cv2.imshow ('image_display', self.get_latest_image())
                else:
                    print "no image"
            except KeyboardInterrupt:
                break;

            # take a rest for a bit
            time.sleep(1)

# run test run from the command line
if __name__ == "__main__":
    sc_webcam0 = PiCam(1)
    sc_webcam0.main()
