
'''base class for all camera implimentations
   -1 on anyvalue means unimplimented, 
   returning false means the operation either failed or is not supported'''

class AnyCamera():
    def __init__(self):
        '''initializtion code'''

    def cameraInit(self):
        ''' camera initial settings, this should be priviate if python allows such a thing'''

    def setGPSCoordinates(self):
        ''' store gps coordinates available for all the camera implimentations downstream'''

    def setAttitude(self):

    def zoomIn(self):

    def zoomOut(self):

    def setExposureMode(self):

    def setShutterSpeed(self):

    def setAperture(self):

    def setISO(self):

    def trigger(self):

    def startStreaming(self, mode, port): // MJPEG/H264, port

    def setIllumination(self, illuminationType): // None/visibile/IR

    def setRecording(self, recording): // only for handycam or video camera

    def setElectronicStabilization(self, stabiliztion): // true/false/on/off

    def cameraID(self): // not sure whether this should be mavlink id or something else

    def getStatus(self): // for sending down the mavlink whether recording is on, aperture etc
