from cv2 import *
from numpy import * 
from numpy.linalg import inv, det
from time import time
import pickle
from sklearn import svm, preprocessing

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

# camera parameters
CAPTURE_WIDTH = 320
CAPTURE_HEIGHT = 240
ROWS = CAPTURE_HEIGHT
COLS = CAPTURE_WIDTH

# HSV thresholds (hue 0-179, saturation 0-255, value 0-255)
HSV_UPPER_LIMIT = (179,255,255) #yellow (56, 255, 255)
HSV_LOWER_LIMIT = (100,100,100) #yellow (26, 50, 100)

# create cross-correlation templates
col_temp = ones((ROWS,1), uint8) #ROWS by 1 array
row_temp = ones((1,COLS), uint8) #1 by COLS array


# configure camera
cam = VideoCapture(0)
cam.set(3, CAPTURE_WIDTH)
cam.set(4, CAPTURE_HEIGHT)

# initialize window
namedWindow("img", cv.CV_WINDOW_AUTOSIZE)
namedWindow("img2", cv.CV_WINDOW_AUTOSIZE)

# first frame assumed to be junk
junk1, junk2 = cam.read()

dt = 1

# Initialize classifier features
xmean = None
xvariance = None
xpeakval = None
x90peakwidth = None
x75peakwidth = None
x50peakwidth = None
ymean = None
yvariance = None
ypeakval = None
y90peakwidth = None
y75peakwidth = None
y50peakwidth = None
sumpixels = None

# open text file and store as python opject, then recover classifier and feature scaler
data_file = open('classifier_and_feature_scaler.txt', 'r')
classifier_and_feature_scaler = pickle.load(data_file)	# features with target present
data_file.close()
classifier = classifier_and_feature_scaler[0]
feature_scaler = classifier_and_feature_scaler[1]

while (True):

	t = time()

	# grab frame and convert to hsv
	s, img = cam.read()
	img2 = img
	img = cvtColor(img, cv.CV_BGR2HSV)

	# apply hsv threshold
	upperb = array(HSV_UPPER_LIMIT, uint8)
	lowerb = array(HSV_LOWER_LIMIT, uint8)
	img = inRange(img, lowerb, upperb)
	#img = medianBlur(img,5)

	# cross-correlate image with templates
	x_ccor = matchTemplate(img, col_temp, cv.CV_TM_CCORR) #1 by COLS array
	y_ccor = matchTemplate(img, row_temp, cv.CV_TM_CCORR) #ROWS by 1 array

	# get x and y cordinates of maximum
	x_minVal, x_maxVal, x_minLoc, x_maxLoc = minMaxLoc(x_ccor) 
	y_minVal, y_maxVal, y_minLoc, y_maxLoc = minMaxLoc(y_ccor)

	x_coord = x_maxLoc[0]
	y_coord = y_maxLoc[1]

	
	xmean = mean(x_ccor)
	xvariance = var(x_ccor)
	xpeakval = x_maxVal
	x90peakwidth = peak_width(x_ccor[0], x_maxLoc[0], .90)
	#x75peakwidth = peak_width(x_ccor[0], x_maxLoc[0], .75)
	#x50peakwidth = peak_width(x_ccor[0], x_maxLoc[0], .50)
	ymean = mean(y_ccor)
	yvariance = var(y_ccor)
	ypeakval = y_maxVal
	y90peakwidth = peak_width(y_ccor, y_maxLoc[1], .90)
	#y75peakwidth = peak_width(y_ccor, y_maxLoc[1], .75)
	#y50peakwidth = peak_width(y_ccor, y_maxLoc[1], .50)
	#sumpixels = sum(x_ccor)

	features = 	[	xmean,
					xvariance,
					xpeakval,
					x90peakwidth,
					#x75peakwidth,
					#x50peakwidth,
					ymean,
					yvariance,
					ypeakval,
					y90peakwidth
					#y75peakwidth,
					#y50peakwidth,
					#sumpixels
					]
 	

	# convert image from grayscale to BGR
	img = cvtColor(img, cv.CV_GRAY2BGR)

	# draw circle centered at maximum
	circle(img, (x_coord, y_coord), 2, cv.CV_RGB(255,0,0), 2) # measured


	# display converted image
	imshow("img", img)
	imshow("img2", img2)
	waitKey(1)

	#determine if target is in frame or not
	if classifier.predict(feature_scaler.transform([features])) == 1:
		target_in_frame = 'TRUE'
	else:
		target_in_frame = 'FALSE'

	print 'Target in frame:	', target_in_frame
	print '(X,Y) MEASURED: 	', (x_coord, y_coord)
	print 'dt: 			', time() - t
