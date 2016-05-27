'''
mavproxy_vision.py
Written by Colin Doolittle and David Wurtz

Official Code Documentation


What does this code do?

---->	mavproxy_vision.py is a color-based computer vision module 
	designed to be used with MAVProxy.py, a Python wrapper that
	establishes a link with the ArduPilot Mega flight board
	(APM2.5). It detects the presence or absence of a familiar 
	target (see Training Classifier section below), and if 
	present, tracks its location. 

---->	When imported into the MAVProxy environment, this module
	will interface the nearest camera and wait until the user
	sets the flightmode to ALT_HOLD on RC channel 5. Channel 6 
	is used to select one of five different hues that the 
	vision system will look for. These hue values must be 
	configured manually by the user (see Hue Selection section
	below).  While ALT_HOLD is the current flightmode, the 
	module will continuously filter, classify, and track the
	camera image.  	

---->	The authors of this module leave it to the MAVProxy
	community to extend the functionality of this computer 
	vision module. The code is currently written for a 
	quadcopter with one camera looking straight downwards, but
	other configurations are possible.

Command-line flags

The version of mavproxy.py located in the same folder as this README
file has new command line options that optimize mavproxy for
embedded applications, such as running this vision module on a 
Raspberry Pi board or other lightweight computer attached to the UAV.
These options are:

	--embedded		Disables the user input thread
	--disable-logging	Disables the log writer thread


Code Dependecies

In addition to MAVProxy's dependecies 
(qgroundcontrol.org/mavlink/mavproxy_startpage) the user must 
install the following packages, ideally in a Linux environment:

	Python-opencv	(opencv.org)
	Numpy		(numpy.org)
	Scikit-Learn	(scikit-learn.org)
	RPi.GPIO	(pypi.python.org/pypi/RPi.GPIO)

RPi.GPIO can be neglected if the user is not running the vision
module on a Raspberry Pi. GPIO code that controls an LED should be 
commented out in this case.


Camera Setup

In mavproxy_vision.py there is a function called init() which
is called when the module is imported.  The vision_state object is
created here, and the line

mpstate.vision_state.cam = VideoCapture(0)

creates the camera object.  The argument to VideoCapture() is set
to zero by default.  This indicates the first element in an array
of cameras that may or may not be connected to the system. For
example, if running MAVProxy on a laptop with a built-in webcam as
well as a USB camera connected, the built-in webcam usually
corresponds to 0 and the USB camera to 1.  

The resolution of the camera image can be set by changing the 
self.CAPTURE_WIDTH and self.CAPTURE_HEIGHT variables in the 
__init__() function of the vision_state class. By default this is
160x120.

  

Hue Selection

The authors of mavproxy_vision.py encourage you to use hsvtool.py,
included in the repository, to help you choose the HSV values that
define your target.  By adjusting six different sliders, the upper 
and lower bounds of the target color can be tweaked until the object 
appears solid white in the display window and everything else is
black.

Up to 5 distinct colors can become the target of the vision system,
by entering your HSV values into the corresponding arrays in the 
update_hue() function in mavproxy_vision.py.  We find that 
fluorescent colors make the best targets as they stand out from
background noise.

By default, the code is written to track fluorescent yellow with the
RC 6 knob turned all the way counter-clockwise, which sets RC 6 = 3,
and track fluorescent pink with the knob turned all the way
clockwise, setting RC 6 = 7.  This makes it easy to be sure about 
which value is selected, as our knob has no demarkations.  You can 
assign values 4, 5, and 6 to other colors by uncommenting that code
section if you like.


Radio setup

After calibrating your RC controller, the APM stores parameters
RC1_TRIM and RC2_TRIM which represent the PWM value sent when the
roll/pitch stick (usually on the right) is centered.  These PWM
values are probably around 1500, but the exact value will be depend
on the individual controller.  These trim values need to be entered
into mavproxy_vision.py as self.ch1_trim and self.ch2_trim.

We recommend also that RC1_DZ and RC2_DZ be set to some low value. 
This is the size of the Dead Zone around the trim value, a lower
value means more responsiveness.


Classifier Training

The mavproxy_vision.py script requires a file called 
'classifier_and_feature_scaler.txt'. This file contains two Putty 
encoded objects: a trained classifier and a feature scaler. Below are
the steps required to generate classifier_and_feature_scaler.txt. 


1. 	For convenience, the following files should be placed in the same
	directory:

	hsvtool.py
	pycvtrainingpositive.py
	pycvtrainingnegative.py
	trainclassifier.py
	vision.py

2. 	Configure camera and color filter parameters

	pycvtrainingpositive.py, pycvtrainingnegative.py, and vision.py
	need to use the same camera and color filter parameters. Use a text
	editor set CAPTURE_WIDTH, CAPTURE_HEIGHT, HSV_UPPER_LIMIT, and 
	HSV_LOWER_LIMIT parameters.

	Capture height and width values must be compatable with your camera.
	Common resolutions include: 160x120, 320x240, 640x480

	Appropriate HSV limits for the color filter can be found by using
	the hsvtool.

3.	Run pycvtrainingpositive.py

	It is very important that your target appears in every single frame,  
	otherwise the accuracy of your classifier will be compromised. While
	the script is running move your target around the frame. Be sure to 
	get along the edges, and to vary your target's distance from the 
	camera. You can run this script as many times as you like. Only the 
	last run's data will be saved.

4. 	Run pycvtrainingnegative.py 

	It is very important that your target does NOT appear in any frame,
	otherwise the accuracy of your classifier will be compromised. While 
	the script is running move your camera around to pick up any stray
	noise that gets through the color filter. You can run this script as 
	many times as you like. Only the last run's data will be saved.

5. 	Run trainclassifier.py

	The script will use data produced in the previous steps to create 
	and export a feature scaler and classifier.

6. 	Run vision.py and check classifier performance

	While the script is running you can move your target into and out
	of the frame. The script will print TRUE if it detects your target
	and FALSE if it doesn't. Test the performance with your target at
	various distances and positions.

	If you feel that your target isn't being detected when it should be,
	try redoing step 3 above then run trainsclassifier.py again.

	If you feel that your target is being falsely detected, try redoing
	step 4 above then run trainclassifier.py again. 

7. 	Copy classifier_and_feature_scaler.txt into the MAVProxy folder

	Once you're satisfied with your classifier move 
	classifier_and_feature_scaler.txt to the same directory as the 
	mavproxy.py file (it should be in a folder called
	MAVProxy).


	


  