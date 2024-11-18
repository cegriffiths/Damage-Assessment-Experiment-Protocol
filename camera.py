## CAMERA SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the camera

from tkinter import *
from PIL import ImageTk, Image, ImageDraw
import os
import DamageInspectionRigApp as DI
import numpy as np

### Directly from James Brown's code
# Create calibration frame image
CALIB_FRAME_SIZE = [376, 524] # Decided in collaboration with Redlen Metrology team
PREVIEW_FRAME_SIZE = [480, 640]
xBorder = int((PREVIEW_FRAME_SIZE[0] - CALIB_FRAME_SIZE[0]) / 2)
yBorder = int(((PREVIEW_FRAME_SIZE[1] - CALIB_FRAME_SIZE[1]) / 2))
SHAPE = [(xBorder, yBorder), (xBorder + CALIB_FRAME_SIZE[0], yBorder + CALIB_FRAME_SIZE[1])]
calibFrameImg = Image.new("RGBA", PREVIEW_FRAME_SIZE) # RGBA for transparent background
calibFrameDraw = ImageDraw.Draw(calibFrameImg)
calibFrameDraw.rectangle(SHAPE, outline='red', width=2)

def assessBrightness(inImage):
    # Quick image analysis
    lightingTestImArr = np.array(inImage)
    # Naive but easy check -> average all pixels within calibration frame that are above some threshold
    WHITE_LIMIT = 150
    count = total = 0
    for r in range(CALIB_FRAME_SIZE[1]):
        for c in range(CALIB_FRAME_SIZE[0]):
            if lightingTestImArr[r + yBorder][c + xBorder][0] > WHITE_LIMIT:
                total += lightingTestImArr[r + yBorder][c + xBorder][0]
                count += 1
    if count>0:            
        averageWhiteVal = int(total / count)
    elif count==0:
        averageWhiteVal = 0
    else:
        averageWhiteVal = -1
    # print(f"AVG PIXEL VALUE: {averageWhiteVal}\nTARGET: 202")
    # print(f"Count: {count}/{CALIB_FRAME_SIZE[1] * CALIB_FRAME_SIZE[0]}")
    return averageWhiteVal
###

class camera:
    '''Camera Object: Controls the camera. Provides a live feed, can take images, can check calibration'''
    def __init__(self):
        self.state = "Init"

        ## For General UI Window
        self.root = Tk()
        # Use an event to pass trigger a UI action when new data is available from the camera
        onLiveImageUpdate = lambda : self.root.event_generate("<<NewLiveImage>>", when="tail")
        self.damageApp = DI.App(onLiveImageUpdate)
        self.root.bind("<<NewLiveImage>>", self.__drawLiveImage)
        # Close the camera stream when the UI closes
        self.root.protocol("WM_DELETE_WINDOW", self.__handleClose)

        self.calibrationOpen = False
        self.imagingOpen = False


    def checkCalibration(self):
        '''Automatically checks calibration of the camera'''
        ## TODO
        print("Calibrating")


    def __drawLiveImage(self, _event):
    # if a new image becomes available: take the latest image and display it
        if self.damageApp.lastFrame is not None:
            img = self.damageApp.lastFrame

            if self.calibrationOpen:
                img.paste(calibFrameImg, mask=calibFrameImg)
                img = ImageTk.PhotoImage(img)
                self.calibrationFeedPanel.configure(image=img)
                self.calibrationFeedPanel.image = img
            elif self.imagingOpen:
                img = ImageTk.PhotoImage(img)
                self.imagingFeedPanel.configure(image=img)
                self.imagingFeedPanel.image = img

    def __handleClose(self, destroy = False):
        # Prevent thread jumping events
        self.root.unbind_all("<<NewLiveImage>>")
        self.damageApp.liveCallback = lambda : None
        # Quit the main loop
        if destroy:
            # Kill UI window, destroy all UI elements, end UI loop
            self.root.destroy()
        else:
            # Kill UI window, end UI loop, (let python clean up UI elements)
            self.root.quit()

    def buildUI(self):
        '''Builds the basic camera window UI. Has the options to open calibration or imaging windows'''
        self.root.title("Camera Window")

        self.openCalButton = Button(self.root, text='Open Calibration', command=self.buildCalibrationUI)
        self.openCalButton.grid(column = 0, row = 0)
        self.openImagingButton = Button(self.root, text='Open Imaging', command=self.buildImagingUI)
        self.openImagingButton.grid(column = 1, row = 0)

    def buildCalibrationUI(self):
        '''Build the calibration window UI for the user to check the camera's calibration. 
        Should display the current frame with rectangle for sensor size comparison, and brightness information.'''
        self.openCalButton.config(state="disabled")
        self.calibrationOpen = True

        self.calibrationWindow = Toplevel(self.root)
        self.calibrationWindow.title("Camera Calibration")
        
        # Calibration Explanation
        textexplanation = Label(self.calibrationWindow, text='Procedure: To check the camera\'s calibration, check that the sensor fits in the red calibration frame, \
check that the brightness is the correct value, and check that the sensor is in focus', wraplength=550, justify="left")
        textexplanation.grid(column=0, row=0)

        # Live Feed
        self.calibrationFeedLabel = Label(self.calibrationWindow, text="Live Feed")
        self.calibrationFeedLabel.grid(column=0, row=1)
        self.calibrationFeedPanel = Label(self.calibrationWindow)
        self.calibrationFeedPanel.grid(column=0, row=2)

        # Lighting Results
        self.brightnessResultLabel = Label(self.calibrationWindow, text='Brightness: 0 / 202')
        self.brightnessResultLabel.grid(column=0, row=3, sticky='W')
        self.getBrightness()

        # Set function for when the window is closed
        self.calibrationWindow.protocol("WM_DELETE_WINDOW", self.on_calibration_close)


    def getBrightness(self):
        '''Get the current brightness value from the camera feed'''
        self.brightnessResultLabel.config(text=f'Brightness: {assessBrightness(self.damageApp.lastFrame)} \t Target Brightness: 202')
        self.calibrationWindow.after(1000, self.getBrightness)

    def on_calibration_close(self):
        '''Set calibration boolean to false, close window, and reset calibration button'''
        self.calibrationOpen = False
        self.calibrationWindow.destroy()
        self.openCalButton.config(state="normal")


    def buildImagingUI(self):
        '''Build the imaging window UI for the user to get feedback while the imaging is taking place. 
        Should display the current frame, and sensor information.'''
        ##FOR NOW
        sensorID = "32wdqisd3"
        numPnP = 232


        self.openImagingButton.config(state="disabled")
        self.imagingOpen = True

        self.imagingWindow = Toplevel(self.root)
        self.imagingWindow.title("Sensor Imaging")
        
        ### Sensor Information ###
        sensorInfoFrame = Frame(self.imagingWindow)
        sensorInfoFrame.grid(column=0, row=0)
        self.sensorIDLabel = Label(sensorInfoFrame, text=f'Sensor ID: {sensorID}')
        self.sensorIDLabel.grid(column=0, row=0)
        self.numPnPLabel = Label(sensorInfoFrame, text=f'Number of PnP cycles performed: {numPnP}')
        self.numPnPLabel.grid(column=0, row=1)

        ### LIVE FEED ###
        imagingFeedFrame = Frame(self.imagingWindow)
        imagingFeedFrame.grid(column=1, row=0)
        self.imagingFeedLabel = Label(imagingFeedFrame, text="Live Feed")
        self.imagingFeedLabel.grid(column=0, row=0)
        self.imagingFeedPanel = Label(imagingFeedFrame)
        self.imagingFeedPanel.grid(column=0, row=1)

        self.imagingWindow.protocol("WM_DELETE_WINDOW", self.on_imaging_close)


    def on_imaging_close(self):
        '''Set imaging boolean to false, close window, and reset imaging button'''
        self.imagingOpen = False
        self.imagingWindow.destroy()
        self.openImagingButton.config(state="normal")

    def takeImage(self):
        print("Snap!")
        self.damageApp.snapImage(os.path.join(self.outputPath, self.sensorList[self.step]['sensor']))
    
    def run(self):
        # self.buildCalibrationUI()
        # self.calDamageApp.run(self.calroot.mainloop)
        self.buildUI()
        self.damageApp.run(self.root.mainloop)


if __name__ == '__main__':
    cam = camera()
    cam.run()
