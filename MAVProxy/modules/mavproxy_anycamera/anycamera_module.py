'''entry point for any camera module having implimentation of various cameras'''

import time, math
from pymavlink import mavutil

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.mp_settings import MPSetting

class AnyCameraModule(mp_module.MPModule, AnyCamera):
    def __init__(self, mpstate):
        super(AnyCameraModule, self).__init__(mpstate, "anycamera", "anycamera commands")
        self.add_command('list', self.cmd_list_cameras, "show all initialized cameras")
        self.camera_list = []
    
    def cmd_list_cameras(self):

    def setGPSCoordinates(self):
        for camera in camera_list:
            camera.setGPSCoordinates()

    def setAttitude(self):
        for camera in camera_list:
            camera.setAttitude()

    def zoomIn(self):
        for camera in camera_list:
            camera.zoomIn()

    def zoomOut(self):
        for camera in camera_list:
            camera.zoomOut()

    def setExposureMode(self):
        for camera in camera_list:
            camera.setExposureMode()

    def setShutterSpeed(self):
        for camera in camera_list:
            camera.setShutterSpeed()

    def setAperture(self):
        for camera in camera_list:
            camera.setAperture()

    def setISO(self):
        for camera in camera_list:
            camera.setISO()

    def trigger(self):
        for camera in camera_list:
            camera.trigger()

    def startStreaming(self, mode, port): // MJPEG/H264, port
        for camera in camera_list:
            camera.startStreaming()

    def setIllumination(self, illuminationType): // None/visibile/IR
        for camera in camera_list:
            camera.setIllumination()

    def setRecording(self, recording): // only for handycam or video camera
        for camera in camera_list:
            camera.setRecording()

    def setElectronicStabilization(self, stabiliztion): // true/false/on/off
        for camera in camera_list:
            camera.setElectronicStabilization()

    def cameraID(self): // not sure whether this should be mavlink id or something else
        for camera in camera_list:
            camera.cameraID()

    def getStatus(self): // for sending down the mavlink whether recording is on, aperture etc
    

     def __vDecodeDIGICAMConfigure(self, mCommand_Long):
        if mCommand_Long.param1 != 0:
            print ("Exposure Mode = %d" % mCommand_Long.param1)
            
            if mCommand_Long.param1 == self.ProgramAuto:
                self.__vCmdSetCamExposureMode(["Program Auto"])
            
            elif mCommand_Long.param1 == self.Aperture:
                self.__vCmdSetCamExposureMode(["Aperture"])
            
            elif mCommand_Long.param1 == self.Shutter:
                self.__vCmdSetCamExposureMode(["Shutter"])

        '''Shutter Speed'''
        if mCommand_Long.param2 != 0:
            print ("Shutter Speed= %d" % mCommand_Long.param2)
            self.__vCmdSetCamShutterSpeed([mCommand_Long.param2])
        
        '''Aperture'''
        if mCommand_Long.param3 != 0:
            print ("Aperture = %d" % mCommand_Long.param3)
            self.__vCmdSetCamAperture([mCommand_Long.param3])

        '''ISO'''
        if mCommand_Long.param4 != 0:
            print ("ISO = %d" % mCommand_Long.param4)
            self.__vCmdSetCamISO([mCommand_Long.param4])

        '''Exposure Type'''
        if mCommand_Long.param5 != 0:
            print ("Exposure type= %d" % mCommand_Long.param5)



    def __vDecodeDIGICAMControl(self, mCommand_Long):
        '''Session'''
        if mCommand_Long.param1 != 0:
            print ("Session = %d" % mCommand_Long.param1)
        
        '''Zooming Step Value'''
        if mCommand_Long.param2 != 0:
            print ("Zooming Step = %d" % mCommand_Long.param2)
        
        '''Zooming Step Value'''
        if mCommand_Long.param3 != 0:
            print ("Zooming Value = %d" % mCommand_Long.param3)

            if (mCommand_Long.param3 == 1):
                self.__vCmdCamZoomIn()
            elif (mCommand_Long.param3 == -1):
                self.__vCmdCamZoomOut()
            else:
                print ("Invalid Zoom Value")
        
        '''Focus 0=Unlock/1=Lock/2=relock'''
        if mCommand_Long.param4 != 0:
            print ("Focus = %d" % mCommand_Long.param4)
        
        '''Trigger'''
        if mCommand_Long.param5 != 0:
            print ("Trigger = %d" % mCommand_Long.param5)
            self.__vCmdCamTrigger(mCommand_Long)



    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        mtype = m.get_type()
        if mtype == "GLOBAL_POSITION_INT":
            for cam in self.camera_list:
                cam.setGPSCoordinates(m)
        if mtype == "ATTITUDE":
            for cam in self.camera_list:
                cam.setAttitude(m)
        if mtype == "CAMERA_STATUS":
            print ("Got Message camera_status")
        if mtype == "CAMERA_FEEDBACK":
            print ("Got Message camera_feedback")
        if mtype == "COMMAND_LONG":
            if m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE:
                print ("Got Message Digicam_configure")
                self.__vDecodeDIGICAMConfigure(m)
            elif m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL:
                print ("Got Message Digicam_control")
                self.__vDecodeDIGICAMControl(m)

def init(mpstate):
    '''initialize module'''
    return AnyCameraModule(mpstate)

