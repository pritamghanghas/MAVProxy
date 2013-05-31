'''
pycvtrainingpositive.py

by David Wurtz, last updated 05-22-13

Running this code will produce a Putty encoded dataset of 'positive' feature vectors.
(positive meaning that the target you are trying to track is present)
'''

from cv2 import *
from numpy import * 
from numpy.linalg import inv, det
from time import time
import pickle

''' returns peak width '''
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

''' camera parameters '''
CAPTURE_WIDTH = 160
CAPTURE_HEIGHT = 120
ROWS = CAPTURE_HEIGHT
COLS = CAPTURE_WIDTH

''' HSV thresholds (hue 0-179, saturation 0-255, value 0-255) '''
HSV_UPPER_LIMIT = (179, 255, 255) 
HSV_LOWER_LIMIT = (169, 50, 100) 

''' create cross-correlation templates '''
col_temp = ones((ROWS,1), uint8) #ROWS by 1 array
row_temp = ones((1,COLS), uint8) #1 by COLS array


''' configure camera '''
cam = VideoCapture(1)
cam.set(3, CAPTURE_WIDTH)
cam.set(4, CAPTURE_HEIGHT)

''' initialize window to dispay image from camera '''
namedWindow("img", cv.CV_WINDOW_AUTOSIZE)

''' first frame assumed to be junk '''
junk1, junk2 = cam.read()

''' Initialize classifier features '''
xmean = None			# mean value of x-histogram
xvariance = None		# variance of x-histogram
xpeakval = None			# max value of x-histogram
x90peakwidth = None		# 90% peak width of x-histogram
ymean = None			# mean value of y-histogram
yvariance = None		# variance of y-histogram
ypeakval = None			# max value of y-histogram
y90peakwidth = None		# 90% peak width of y-histogram

dataset = []			# matrix of feature vectors

''' collect 1000 lines of data '''
for i in range(0,1000):

	''' used to calculate loop time '''
	t = time()

	''' grab frame and convert to hsv '''
	s, img = cam.read()
	img = cvtColor(img, cv.CV_BGR2HSV)

	''' apply hsv threshold '''
	upperb = array(HSV_UPPER_LIMIT, uint8)
	lowerb = array(HSV_LOWER_LIMIT, uint8)
	img = inRange(img, lowerb, upperb)

	''' cross-correlate image with templates to generate x and y histograms '''
	x_ccor = matchTemplate(img, col_temp, cv.CV_TM_CCORR) # 1 by COLS array
	y_ccor = matchTemplate(img, row_temp, cv.CV_TM_CCORR) # ROWS by 1 array

	''' get x and y cordinates of maximum (this is presumed to be the target location) '''
	x_minVal, x_maxVal, x_minLoc, x_maxLoc = minMaxLoc(x_ccor) 
	y_minVal, y_maxVal, y_minLoc, y_maxLoc = minMaxLoc(y_ccor)
	x_coord = x_maxLoc[0]
	y_coord = y_maxLoc[1]

	''' compute features and create feature vector, add vector to dataset '''
	xmean = mean(x_ccor)
	xvariance = var(x_ccor)
	xpeakval = x_maxVal
	x90peakwidth = peak_width(x_ccor[0], x_maxLoc[0], .90)
	ymean = mean(y_ccor)
	yvariance = var(y_ccor)
	ypeakval = y_maxVal
	y90peakwidth = peak_width(y_ccor, y_maxLoc[1], .90)

	features = 	[	xmean,
					xvariance,
					xpeakval,
					x90peakwidth,
					ymean,
					yvariance,
					ypeakval,
					y90peakwidth]

	dataset.append(features)

	''' print computed features from this frame '''
	print 'xmean:			', xmean
	print 'xvariance:		', xvariance
	print 'xpeakval:		', xpeakval
	print 'x90peakwidth:	', x90peakwidth
	print 'ymean:			', ymean
	print 'yvariance:		', yvariance
	print 'ypeakval:		', ypeakval
	print 'y90peakwidth:	', y90peakwidth

	''' convert image from grayscale to BGR '''
	img = cvtColor(img, cv.CV_GRAY2BGR)

	''' draw circle centered at maximum '''
	circle(img, (x_coord, y_coord), 2, cv.CV_RGB(255,0,0), 2) # measured target location

	''' display converted image '''
	imshow("img", img)
	waitKey(1)

	''' print the measured target location and loop time '''
	print '(X,Y) MEASURED: 	', (x_coord, y_coord)
	print 'dt: 			', time() - t

''' export data '''
data_file = open('training_positive.txt', 'w+')
data_file.write(pickle.dumps(dataset))
data_file.close