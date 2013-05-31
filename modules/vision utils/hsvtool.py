'''
HSV Color filter tool

by Colin Doolittle and David Wurtz, last updated 05-22-13

This tool helps you determine HSV color filter thresholds with a 
graphical interface and camera feedback.
'''

from cv2 import *
from Tkinter import *
from numpy import *
import threading
from time import sleep

''' camera parameters '''
CAPTURE_WIDTH = 360
CAPTURE_HEIGHT = 240

''' HSV thresholds (hue 0-179, saturation 0-255, value 0-255) '''
HSV_UPPER_LIMIT = [179,255,255] #yellow (56, 255, 255)
HSV_LOWER_LIMIT = [160,100,100] #yellow (26, 50, 100)

''' configure camera '''
cam = VideoCapture(0)
cam.set(3, CAPTURE_WIDTH)
cam.set(4, CAPTURE_HEIGHT)

''' initialize windows '''
namedWindow("img", cv.CV_WINDOW_AUTOSIZE)
namedWindow("img2", cv.CV_WINDOW_AUTOSIZE)

''' this function continuously grabs frames from the webcam. It gets threaded,
the count prevents it from completely bogging down the cpu '''
def get_frame():
    count = 1
    while 1:
        if (count % 50 == 0):
            count = 1	# reset count

            ''' grab frame and convert to hsv '''
            s, img = cam.read()
            img2 = img
            img = cvtColor(img, cv.CV_BGR2HSV)

            ''' apply hsv threshold '''
            upperb = array(HSV_UPPER_LIMIT, uint8)
            lowerb = array(HSV_LOWER_LIMIT, uint8)
            img = inRange(img, lowerb, upperb)

            ''' display converted original image '''
            imshow("img", img)
            imshow("img2", img2)
            waitKey(1)

        else:
            count += 1



class App(object):

    def __init__(self, master):

        frame = Frame(master, background='black', padx=2, pady=10)
        frame.grid()

        ''' upper title '''
        self.upper_limit = Label(frame,
                           text="Upper Limit",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.upper_limit.grid(row=0, column=1)   

        ''' upper h stuff '''
        self.upper_h = Label(frame,
                           text="H:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.upper_h.grid(row=1, column=0)   

        self.upper_h_scale = Scale(frame,
                  from_ = 0,
                  to = 179,
                  command=self.update_uh,
                  orient=HORIZONTAL)
        self.upper_h_scale.set(179)
        self.upper_h_scale.grid(row=1, column=1)

        ''' upper s stuff '''
        self.upper_s = Label(frame,
                           text="S:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.upper_s.grid(row=2, column=0)

        self.upper_s_scale = Scale(frame,
                  from_ = 0,
                  to = 255,
                  command=self.update_us,
                  orient=HORIZONTAL)
        self.upper_s_scale.set(255)
        self.upper_s_scale.grid(row=2, column=1)

        ''' upper v stuff '''
        self.upper_v = Label(frame,
                           text="V:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.upper_v.grid(row=3, column=0)

        self.upper_v_scale = Scale(frame,
                  from_ = 0,
                  to = 255,
                  command=self.update_uv,
                  orient=HORIZONTAL)
        self.upper_v_scale.set(255)
        self.upper_v_scale.grid(row=3, column=1)

        ''' lower title '''
        self.lower_limit = Label(frame,
                           text="Lower Limit",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.lower_limit.grid(row=4, column=1)   

        ''' lower h stuff '''
        self.lower_h = Label(frame,
                           text="H:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.lower_h.grid(row=5, column=0)   

        self.lower_h_scale = Scale(frame,
                  from_ = 0,
                  to = 179,
                  command=self.update_lh,
                  orient=HORIZONTAL)
        self.lower_h_scale.grid(row=5, column=1)

        ''' lower s stuff '''
        self.lower_s = Label(frame,
                           text="S:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.lower_s.grid(row=6, column=0)

        self.lower_s_scale = Scale(frame,
                  from_ = 0,
                  to = 255,
                  command=self.update_ls,
                  orient=HORIZONTAL)
        self.lower_s_scale.grid(row=6, column=1)

        ''' lower v stuff '''
        self.lower_v = Label(frame,
                           text="V:",
                           font=('Helvetica',16),
                           foreground='white',
                           background='black',
                           padx=5,
                           pady=15)
        self.lower_v.grid(row=7, column=0)

        self.lower_v_scale = Scale(frame,
                  from_ = 0,
                  to = 255,
                  command=self.update_lv,
                  orient=HORIZONTAL)
        self.lower_v_scale.grid(row=7, column=1)

    def update_uh(self, master):
        val = self.upper_h_scale.get()
        HSV_UPPER_LIMIT[0] = val

    def update_us(self, master):
        val = self.upper_s_scale.get()
        HSV_UPPER_LIMIT[1] = val

    def update_uv(self, master):
        val = self.upper_v_scale.get()
        HSV_UPPER_LIMIT[2] = val

    def update_lh(self, master):
        val = self.lower_h_scale.get()
        HSV_LOWER_LIMIT[0] = val

    def update_ls(self, master):
        val = self.lower_s_scale.get()
        HSV_LOWER_LIMIT[1] = val


    def update_lv(self, master):
        val = self.lower_v_scale.get()
        HSV_LOWER_LIMIT[2] = val
        
if __name__ == '__main__':
    '''initialize module'''
    
    ''' thread the get_frame loop '''
    camera_thread = threading.Thread(target=get_frame)
    camera_thread.daemon = True
    camera_thread.start()

    root = Tk()
    hsvtool = App(root)
    root.mainloop()
    