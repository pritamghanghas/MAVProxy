"""
sc_webcam.py

This file includes functions to:
    initialise a web cam
    capture image from web cam

Image size is held in the smart_camera.cnf
"""

import sys
import time
import math
import cv2
import sc_config
import os
from gi.repository import GExiv2
from subprocess import call
import picamera

class PiCam:

    def __init__(self, instance):

        # health
        self.healthy = False;

        # record instance
        self.instance = instance
        self.config_group = "camera%d" % self.instance

        # get image resolution
        self.img_width = sc_config.config.get_integer(self.config_group,'width',3280)
        self.img_height = sc_config.config.get_integer(self.config_group,'height',2464)
        self.camera_name = sc_config.config.get_string(self.config_group, 'camera_name', 'picam')
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

        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.img_width, self.img_height)

        # latest image captured
        self.latest_image = None

    # __str__ - print position vector as string
    def __str__(self):
        return "SmartCameraWebCam Object W:%d H:%d" % (self.img_width, self.img_height)

    def boSet_GPS(self, mGPSMessage):
        if mGPSMessage.get_type() == 'GLOBAL_POSITION_INT':
            (self.vehicleLat, self.vehicleLon, self.vehicleHdg, self.vehicleAMSL) = (mGPSMessage.lat*1.0e-7, mGPSMessage.lon*1.0e-7, mGPSMessage.hdg*0.01, mGPSMessage.alt*0.001)

    # latest_image - returns latest image captured and write it to file
    def get_latest_image(self):
        # write to file
        #create folder for this session
        session_dir = os.path.join(self.photos_dir, str(self.instance))
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        imgfilename = "img-%d.jpg" % (self.get_image_counter())
        complete_filename = os.path.join(session_dir,imgfilename)
        print (complete_filename)
        self.camera.capture(complete_filename)
        exif = GExiv2.Metadata(complete_filename)
        exif.set_gps_info(self.vehicleLon, self.vehicleLat, self.vehicleAMSL)
        exif.save_file()
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
            # send request to image capture for image
            if self.take_picture():
                # display image
                print("took one picture")
#                cv2.imshow ('image_display', self.get_latest_image())
            else:
                print "no image"

            # check for ESC key being pressed
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break

            # take a rest for a bit
            time.sleep(0.01)

# run test run from the command line
if __name__ == "__main__":
    sc_webcam0 = PiCam(1)
    sc_webcam0.main()
