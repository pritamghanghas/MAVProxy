''' 
mavproxy_vision.py
LAST UPDATED 2013/06/21 2:00 PM
written by Colin Doolittle and David Wurtz

Portland State University 2013 Capstone Project

By importing this module in mavproxy.py, the user can engage/disengage a 
color-based computer vision system on channel 5, and use channel 6 to select
which color to track.

Released under the GNU GPL licence
'''

from cv2 import *
from numpy import * 
from numpy.linalg import inv, det
from time import time, sleep
from sklearn import preprocessing, svm
from collections import deque
import pickle
import threading
#import RPi.GPIO as GPIO

# only for Raspberry Pi LED indicator
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(11,GPIO.OUT)

mpstate = None

class vs(object):
    def __init__(self):

        # camera parameters
        self.cam = None
        self.most_recent = None
        self.CAPTURE_WIDTH = 160.0
        self.CAPTURE_HEIGHT = 120.0
        self.HALF_CAPTURE_WIDTH = self.CAPTURE_WIDTH/2
        self.HALF_CAPTURE_HEIGHT = self.CAPTURE_HEIGHT/2

        #HSV thresholds (hue: 0-179, saturation: 0-255, value: 0-255)
        self.color_3_upper_limit = (36, 255, 255)   # yellow
        self.color_3_lower_limit = (25, 100, 100)   # yellow
        self.color_5_upper_limit = (80, 255, 255)   # green
        self.color_5_lower_limit = (60,  100, 75)  # green
        self.color_7_upper_limit = (179, 255, 255)  # pink
        self.color_7_lower_limit = (120, 10, 100)  # pink

        # hue currently selected for tracking, init to pink
        self.HSV_UPPER_LIMIT = self.color_7_upper_limit
        self.HSV_LOWER_LIMIT = self.color_7_lower_limit

        #create cross-correlation templates
        self.col_temp = ones((self.CAPTURE_HEIGHT,1), uint8) #ROWS by 1 array
        self.row_temp = ones((1,self.CAPTURE_WIDTH), uint8) #1 by COLS array

        # for keeping track of vision loop speed
        self.t = 0

        # open text file and store as python opject, then recover classifier and feature scaler
        self.data_file = open('classifier_and_feature_scaler.txt', 'r')
        self.classifier_and_feature_scaler = pickle.load(self.data_file)# features with target present
        self.data_file.close()
        self.classifier = self.classifier_and_feature_scaler[0]
        self.feature_scaler = self.classifier_and_feature_scaler[1]

        # classifier output
        self.target_in_frame = False

        # RC radio data, must reflect your unique settings!
        self.ch1_trim = 1502
        self.ch2_trim = 1510

        # hue parameters
        self.tracking_hue = 'Color 7'
        self.hue = 7 

        # Initialize PID coefficients
        self.x_Ap = 0.7
        self.x_Ai = 0.05
        self.x_Ad = 0.6
        self.y_Ap = 0.8
        self.y_Ai = 0.05
        self.y_Ad = 0.6

        # initialize errors
        self.x_error = 0
        self.y_error = 0
        self.old_x_error = 0
        self.old_y_error = 0

        # initialize error accumulators
        self.x_sigma = deque([0,0,0,0])
        self.y_sigma = deque([0,0,0,0])

        # initialize deltas
        self.x_delta = 0
        self.y_delta = 0

        # initialize timer
        self.t = time()
        self.dt = 0.5

        # flag for pid first output behavior
        self.delta_flag = True
        self.sigma_flag = True


# A local copy of send_rc_override() in MAVProxy
def send_motor_override():
    if mpstate.sitl_output:
        buf = struct.pack('HHHHHHHH',*mpstate.status.override)
        mpstate.sitl_output.write(buf)
    else:
        mpstate.master().mav.rc_channels_override_send(mpstate.status.target_system,
                                                    mpstate.status.target_component,
                                                    *mpstate.status.override)

# threaded in __init__
def vision_loop():
    while 1:
        if mpstate.status.flightmode == 'ALT_HOLD':
            track()

# threaded in __init__
def camera_loop():
    while 1:
        s, mpstate.vs.most_recent = mpstate.vs.cam.read()
        sleep(.05)

# returns n% peak width
def peak_width(curve, peak_index, percent):
    x = peak_index

    upper_index = 0
    lower_index = 0
    while (x < size(curve)):
        if (curve[x] > percent*curve[peak_index]):
            x += 1
        else:
            upper_index = x
            break

    x = peak_index
    while (x > 0):
        if (curve[x] > percent*curve[peak_index]):
            x -= 1
        else:
            lower_index = x
            break

    return (upper_index - lower_index)

def name():
    '''return module name'''
    return "vision"

def description():
    '''return module description'''
    return "This module tracks an object based on its HSV specs"

def init(_mpstate):
    '''initialize module'''
    global mpstate
    mpstate = _mpstate
    mpstate.vs = vs()

    # thread the vision loop
    vision_thread = threading.Thread(target=vision_loop)
    vision_thread.daemon = True
    vision_thread.start()

    '''initialize camera'''
    try:
        mpstate.vs.cam = VideoCapture(0)
    except:
        print("Could not initialize camera")
    mpstate.vs.cam.set(3, mpstate.vs.CAPTURE_WIDTH)
    mpstate.vs.cam.set(4, mpstate.vs.CAPTURE_HEIGHT)
    print("vision initialized")

    # thread the camera loop
    camera_thread = threading.Thread(target=camera_loop)
    camera_thread.daemon = True
    camera_thread.start()

def update_hue(hue_int):
    '''update tracking hue based on RC channel 6'''
    if hue_int != mpstate.vs.hue:
        mpstate.vs.hue = hue_int
        if hue_int == 3: 
            mpstate.vs.HSV_UPPER_LIMIT = mpstate.vs.color_3_upper_limit
            mpstate.vs.HSV_LOWER_LIMIT = mpstate.vs.color_3_lower_limit
            mpstate.vs.tracking_hue = 'Color 3'
        elif hue_int == 5:
            mpstate.vs.HSV_UPPER_LIMIT = mpstate.vs.color_5_upper_limit
            mpstate.vs.HSV_LOWER_LIMIT = mpstate.vs.color_5_lower_limit
            mpstate.vs.tracking_hue = 'Color 5'
        elif hue_int == 7:
            mpstate.vs.HSV_UPPER_LIMIT = mpstate.vs.color_7_upper_limit
            mpstate.vs.HSV_LOWER_LIMIT = mpstate.vs.color_7_lower_limit
            mpstate.vs.tracking_hue = 'Color 7'
        else: 
            pass

def track():
    '''isolate target hue, classify target detection, send rc override'''

    # grab frame and convert to hsv
    img = cvtColor(mpstate.vs.most_recent, cv.CV_BGR2HSV)
    
    # apply hsv threshold
    upperb = array(mpstate.vs.HSV_UPPER_LIMIT, uint8)
    lowerb = array(mpstate.vs.HSV_LOWER_LIMIT, uint8)
    img = inRange(img, lowerb, upperb)

    # cross-correlate image with templates
    x_ccor = matchTemplate(img, mpstate.vs.col_temp, cv.CV_TM_CCORR) #1 by COLS array
    y_ccor = matchTemplate(img, mpstate.vs.row_temp, cv.CV_TM_CCORR) #ROWS by 1 array

    # get x and y cordinates of maximum
    x_minVal, x_maxVal, x_minLoc, x_maxLoc = minMaxLoc(x_ccor) 
    y_minVal, y_maxVal, y_minLoc, y_maxLoc = minMaxLoc(y_ccor)
    x_coord = x_maxLoc[0]
    y_coord = y_maxLoc[1] 

    # Classifier
    xmean = mean(x_ccor)
    xvariance = var(x_ccor)
    xpeakval = x_maxVal
    x90peakwidth = peak_width(x_ccor[0], x_maxLoc[0], .90)
    ymean = mean(y_ccor)
    yvariance = var(y_ccor)
    ypeakval = y_maxVal
    y90peakwidth = peak_width(y_ccor, y_maxLoc[1], .90)
    

    features =[ xmean,
                xvariance,
                xpeakval,
                x90peakwidth,
                ymean,
                yvariance,
                ypeakval,
                y90peakwidth
                ]

    # determine if target is in frame or not
    if mpstate.vs.classifier.predict(mpstate.vs.feature_scaler.transform([features])) == 1:
        mpstate.vs.target_in_frame = True
    else:
        mpstate.vs.target_in_frame = False

    if mpstate.vs.target_in_frame == True and mpstate.status.flightmode == 'ALT_HOLD':
        
        ''' PID Controller for Navigation '''
        # normalize x_error and y_error
        mpstate.vs.x_error = (x_coord - mpstate.vs.HALF_CAPTURE_WIDTH)/mpstate.vs.HALF_CAPTURE_WIDTH
        mpstate.vs.y_error = (mpstate.vs.HALF_CAPTURE_HEIGHT - y_coord)/mpstate.vs.HALF_CAPTURE_HEIGHT
        print 'x_error:     ', mpstate.vs.x_error
        print 'y_error:     ', mpstate.vs.y_error

        # compute deltas
        mpstate.vs.x_delta = (mpstate.vs.x_error - mpstate.vs.old_x_error)/mpstate.vs.dt
        mpstate.vs.y_delta = (mpstate.vs.y_error - mpstate.vs.old_y_error)/mpstate.vs.dt
        if mpstate.vs.delta_flag == True:    # initial deltas are undefined because dt is undefined
            mpstate.vs.x_delta = 0
            mpstate.vs.y_delta = 0
            mpstate.vs.delta_flag = False    # subsequent deltas are defined

        print 'x_delta:     ', mpstate.vs.x_delta
        print 'y_delta:     ', mpstate.vs.y_delta

        # update accumulators
        mpstate.vs.x_sigma.pop()
        mpstate.vs.x_sigma.appendleft(mpstate.vs.x_error*mpstate.vs.dt)
        mpstate.vs.y_sigma.pop()
        mpstate.vs.y_sigma.appendleft(mpstate.vs.y_error*mpstate.vs.dt)
        if mpstate.vs.sigma_flag == True:    # initial sigmas are undefined because dt is undefined
            mpstate.vs.x_sigma = deque([0,0,0,0])
            mpstate.vs.y_sigma = deque([0,0,0,0])
            mpstate.vs.sigma_flag = False    # subsequent sigmas are defined
        print 'x_sigma:     ', mpstate.vs.x_sigma
        print 'y_sigma:     ', mpstate.vs.y_sigma

        # compute pulse
        mpstate.vs.x_pulse = mpstate.vs.x_Ap * mpstate.vs.x_error + mpstate.vs.x_Ai * sum(mpstate.vs.x_sigma) + mpstate.vs.x_Ad * mpstate.vs.x_delta
        mpstate.vs.y_pulse = mpstate.vs.y_Ap * mpstate.vs.y_error + mpstate.vs.y_Ai * sum(mpstate.vs.y_sigma) + mpstate.vs.y_Ad * mpstate.vs.y_delta 

        # motor overrides
        roll_pwm = mpstate.vs.ch1_trim + int(mpstate.vs.x_pulse*50)
        pitch_pwm = mpstate.vs.ch2_trim - int(mpstate.vs.y_pulse*50)
        print 'roll_pwm:        ', roll_pwm
        print 'pitch_pwm:       ', pitch_pwm

        # send a sequence of commands that accelerates and brakes the quadcopter
        #GPIO.output(11,1)
        mpstate.status.override = [roll_pwm,pitch_pwm,0,0,0,0,0,0]
        send_motor_override()  # start movement
        sleep(0.3)             # wait

        mpstate.status.override = [mpstate.vs.ch1_trim,
                                    mpstate.vs.ch2_trim,0,0,0,0,0,0]
        send_motor_override()  # stop brake
        sleep(0.3)             # wait
    else:
        # release to RC radio
        #GPIO.output(11,0)
        mpstate.status.override = [0,0,0,0,0,0,0,0]
        send_motor_override()
        # reset pid
        mpstate.vs.x_sigma = deque([0,0,0,0])
        mpstate.vs.y_sigma = deque([0,0,0,0])
        mpstate.vs.old_x_error = 0
        mpstate.vs.old_y_error = 0
        mpstate.vs.dt = 0.5
        mpstate.vs.delta_flag = True
        mpstate.vs.sigma_flag = True

    mpstate.vs.old_x_error = mpstate.vs.x_error
    mpstate.vs.old_y_error = mpstate.vs.y_error
    mpstate.vs.dt = time() - mpstate.vs.t
    mpstate.vs.t = time()



def mavlink_packet(m):
    '''update color filter hue'''
    if m.get_type() == 'RC_CHANNELS_RAW':       
        rc_temp = m.get_payload()
        the_hue = rc_temp[15]  # grabs the int on ch6
        update_hue(the_hue)
