## CAMERA SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the camera

from tkinter import *
from PIL import ImageTk, Image, ImageDraw
import os
import DamageInspectionRigApp as DI

class camera:
    '''Camera Object: Controls the camera. Provides a live feed, can take images, can check calibration'''
    def __init__(self):
        ## TODO
        self.state = "Init"
        self.root = Tk()
        # Use an event to pass trigger a UI action when new data is available from the camera
        onLiveImageUpdate = lambda : self.root.event_generate("<<NewLiveImage>>", when="tail")
        self.damageApp = DI.App(onLiveImageUpdate)
        self.root.bind("<<NewLiveImage>>", self.__drawLiveImage)
        # Close the camera stream when the UI closes
        self.root.protocol("WM_DELETE_WINDOW", self.__handleClose)

    def checkCalibration(self):
        '''Checks calibration of the camera'''
        ## TODO
        print("Calibration")

    def snap(self):
        '''Takes an image'''
        ## TODO

    def feed(self):
        '''Provides a camera feed'''
        ## TODO

    def __drawLiveImage(self, _event):
    # if a new image becomes available: take the latest image and display it
        if self.damageApp.lastFrame is not None:
            img = self.damageApp.lastFrame
            img = ImageTk.PhotoImage(img)
            self.liveFeedPanel.configure(image=img)
            self.liveFeedPanel.image = img

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
        #### Side Frame ####
        self.SideFrame = Frame(self.root)
        self.SideFrame.grid(column=0, row=1)

        #### TOP BAR ####
        TopBar = Frame(self.root)
        TopBar.grid(column=0, row=0)
        title = Label(TopBar, text = "Damage Assessment Rig - Manual Batch Processing UI\nRedlen Technologies")
        title.grid(column=0, row=0, columnspan=3)

        rdLabel = Label(TopBar, text = 'Round')
        rdLabel.grid(column=0, row=1)
        self.roundCounter = Spinbox(TopBar, from_=0, to=100, width=10, relief='sunken')
        self.roundCounter.grid(column=1, row=1)

        self.startButton = Button(TopBar, text="Start", background='green', command=self.__startCallback)
        self.startButton.grid(column=4, row=1)

        #### SNAP BUTTON ####
        self.snapButton = Button(self.root, text="Snap Image", background='Yellow', borderwidth=5, relief='raised', command=self.__snapImage)
        self.snapButton.grid(column=0, row=3, columnspan=2)
        self.snapButton.configure(state='disabled')

        ### LIVE FEED ####
        liveFeedFrame = Frame(self.root)
        liveFeedFrame.grid(column=2, row=1)
        self.liveFeedLabel = Label(liveFeedFrame, text="Live Feed")
        self.liveFeedLabel.grid(column=0, row=0, columnspan=3)
        self.liveFeedPanel = Label(liveFeedFrame)
        self.liveFeedPanel.grid(column=0, row=1, columnspan=3)

        self.root.title("Redlen Technologies - Damage Assessment Rig")

    def __startCallback(self):
        '''Click handler for start button.'''
        # Start button doubles as Stop button
        if self.state == "STARTED":
            # Stop program when stop button clicked
            return self.__handleClose()
        self.state = "STARTED"
        # Change button to stop button
        self.startButton.config(background='red', text="Stop")
        self.step = 0
        # Allow user to snap images
        self.snapButton.configure(state='normal')

    def __snapImage(self):
        print("Snap!")
        self.damageApp.snapImage(os.path.join(self.outputPath, self.sensorList[self.step]['sensor']))
    
    def run(self):
        self.buildUI()
        self.damageApp.run(self.root.mainloop)


if __name__ == '__main__':
    cam = camera()
    cam.run()
