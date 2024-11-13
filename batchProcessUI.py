# DAMAGE INSPECTION RIG - MANUAL BATCH PROCESSING UI
# Author: James Brown, Manufacturing Automation Engineer
# Date: September 16, 2024
# Redlen Technologies

# UI to assist with image capture of array of sensors on a GelPak.
# Users provide an input CSV that defines sensor array.
# UI enables selecting imaging round, input CSV.
# UI creates/overwrites output folders, snaps images and saves them correctly.
# UI provides simple calibration tools to ensure images are consistent.

from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image, ImageDraw
import csv
import os
import DamageInspectionRigApp as DI
import numpy as np

#### CONSTANTS ####
INPUT_FILES_DIR_NAME = 'INPUT_CSV'
OUTPUT_FILES_DIR_NAME = 'OUTPUT_IMAGES'

def findInputFiles():
    '''Find and return (string, no extension) input CSV files.'''
    csvFiles = list()
    for infile in os.listdir(INPUT_FILES_DIR_NAME):
        if infile.endswith('.csv'):
            csvFiles.append(infile[:-4])
    return csvFiles

def loadGrid(frame, csvName):
    '''Load and show sensor grid UI.'''
    # Get Read CSV, draw labels, box label 1
    sensors = list()
    with open(f'{INPUT_FILES_DIR_NAME}/{csvName}.csv', newline='', encoding='utf-8') as csvfile:
        sensorReader = csv.reader(csvfile, delimiter=',')
        rowCount = colCount = totCount = 0
        for row in sensorReader:
            colCount = 0
            for sensorName in row:
                sensorName = sensorName.lstrip()
                tempFrame = Frame(frame)
                sensors.append({
                    'label': Label(tempFrame, text=sensorName),
                    'frame': tempFrame,
                    'sensor': sensorName
                })
                sensors[totCount]['frame'].grid(column=colCount, row=rowCount)
                sensors[totCount]['label'].grid(column=0, row=0)
                colCount += 1
                totCount += 1
            rowCount += 1
    sensors[0]['frame'].config(borderwidth=5, relief='solid')
    return sensors

def stepGrid(sensors, step):
    '''Iterate sensor grid UI to highlight next sensor.'''
    sensors[step-1]['label'].config(fg='#a4a2a8')
    sensors[step-1]['frame'].config(borderwidth=0)
    sensors[step]['frame'].config(borderwidth=5, relief='solid')

def setupOutputDirectory(round, csvName):
    '''Create or overwrite output images directory.'''
    ROUND_PATH_NAME = "Baseline" if round == "0" else f"Round_{round}"
    imagePath = os.path.join(OUTPUT_FILES_DIR_NAME, ROUND_PATH_NAME, csvName)
    if os.path.exists(imagePath):
        overWrite = messagebox.askokcancel("Warning!", f"Directory already exists for: {csvName} ({ROUND_PATH_NAME}). Do you want to overwrite it?")
        if not overWrite:
            return False, ""
    else:
        try:
            os.makedirs(imagePath)
        except:
            print("Failed to make output directory")
            return False, ""
    return True, imagePath

# Create calibration frame image
CALIB_FRAME_SIZE = [376, 524] # Decided in collaboration with Redlen Metrology team
PREVIEW_FRAME_SIZE = [480, 640]
xBorder = int((PREVIEW_FRAME_SIZE[0] - CALIB_FRAME_SIZE[0]) / 2)
yBorder = int(((PREVIEW_FRAME_SIZE[1] - CALIB_FRAME_SIZE[1]) / 2))
SHAPE = [(xBorder, yBorder), (xBorder + CALIB_FRAME_SIZE[0], yBorder + CALIB_FRAME_SIZE[1])]
calibFrameImg = Image.new("RGBA", PREVIEW_FRAME_SIZE) # RGBA for transparent background
calibFrameDraw = ImageDraw.Draw(calibFrameImg)
calibFrameDraw.rectangle(SHAPE, outline='red', width=4)

def assessLighting(inImage):
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
    averageWhiteVal = int(total / count)
    # print(f"AVG PIXEL VALUE: {averageWhiteVal}\nTARGET: 202")
    # print(f"Count: {count}/{CALIB_FRAME_SIZE[1] * CALIB_FRAME_SIZE[0]}")
    return averageWhiteVal

class BatchProcessUI:
    def __init__(self):
        self.root = Tk()
        self.state = "PREP"
        self.showCalibFrame = False
        self.testLighting = False
        self.inputCsvOptions = findInputFiles()
        # Use an event to pass trigger a UI action when new data is available from the camera
        onLiveImageUpdate = lambda : self.root.event_generate("<<NewLiveImage>>", when="tail")
        self.damageApp = DI.App(onLiveImageUpdate)
        self.root.bind("<<NewLiveImage>>", self.__drawLiveImage)
        # Close the camera stream when the UI closes
        self.root.protocol("WM_DELETE_WINDOW", self.__handleClose)
    
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
    
    def run(self):
        '''Run the main UI loop and start the camera background thread.'''
        self.__buildUiCore()
        self.damageApp.run(self.root.mainloop)

    def __buildUiCore(self):
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

        sensorLabel = Label(TopBar, text = 'Sensor CSV')
        sensorLabel.grid(column=2, row=1)
        self.csvVar = StringVar()
        self.csvDrop = OptionMenu(TopBar, self.csvVar, *self.inputCsvOptions)
        self.csvDrop.grid(column=3, row=1)

        self.startButton = Button(TopBar, text="Start", background='green', command=self.__startCallback)
        self.startButton.grid(column=4, row=1)

        #### SNAP BUTTON ####
        self.snapButton = Button(self.root, text="Snap Image", background='Yellow', borderwidth=5, relief='raised', command=self.__snapImage)
        self.snapButton.grid(column=0, row=3, columnspan=2)
        self.snapButton.configure(state='disabled')

        #### LIVE FEED ####
        liveFeedFrame = Frame(self.root)
        liveFeedFrame.grid(column=2, row=1)
        self.liveFeedLabel = Label(liveFeedFrame, text="Live Feed")
        self.liveFeedLabel.grid(column=0, row=0, columnspan=3)
        self.liveFeedPanel = Label(liveFeedFrame)
        self.liveFeedPanel.grid(column=0, row=1, columnspan=3)
        self.calibButton = Button(liveFeedFrame, text="Show calibration frame", background='yellow', command=self.__calibCallback)
        self.calibButton.grid(column=0, row=2)
        self.lightingTestButton = Button(liveFeedFrame, text="Test lighting", background='yellow', command=self.__lightingCallback)
        self.lightingTestButton.grid(column=1, row=2)
        self.lightingResultLabel = Label(liveFeedFrame, text="")
        self.lightingResultLabel.grid(column=2, row=2)

        self.root.title("Redlen Technologies - Damage Assessment Rig")
    
    def __calibCallback(self):
        '''Show or hide the size calibration frame.'''
        self.showCalibFrame = not self.showCalibFrame
        self.calibButton.config(text=f"{'Hide' if self.showCalibFrame else 'Show'} calibration frame")
    
    def __lightingCallback(self):
        '''Test lighting value. Inefficient and wasteful. Would not leave on.'''
        self.testLighting = not self.testLighting
        self.lightingTestButton.config(text=f"{'Stop' if self.testLighting else 'Start'} Lighting Test")
        self.__checkLighting()
        
    
    def __checkLighting(self):
        if self.testLighting:
            self.lightingResultLabel.config(text=f'Brightness: {assessLighting(self.damageApp.lastFrame)} / 202')
            self.root.after(1000, self.__checkLighting)

    def __drawLiveImage(self, _event):
        # if a new image becomes available: take the latest image and display it
        if self.damageApp.lastFrame is not None:
            img = self.damageApp.lastFrame
            if self.showCalibFrame:
                img.paste(calibFrameImg, mask=calibFrameImg)
            img = ImageTk.PhotoImage(img)
            self.liveFeedPanel.configure(image=img)
            self.liveFeedPanel.image = img

    def __startCallback(self):
        '''Click handler for start button.'''
        # Start button doubles as Stop button
        if self.state == "STARTED":
            # Stop program when stop button clicked
            return self.__handleClose()
        self.state = "STARTED"
        # Change button to stop button
        self.startButton.config(background='red', text="Stop")
        # Load the sensor grid from the selected CSV
        self.sensorList = loadGrid(self.SideFrame, self.csvVar.get())
        self.step = 0
        # Grey out inputs in topbar
        self.roundCounter.configure(state='disabled')
        self.csvDrop.configure(state='disabled')
        # Attempt to find matching dir and prompt warning if exists, else create
        success, self.outputPath = setupOutputDirectory(self.roundCounter.get(), self.csvVar.get())
        if not success:
            return self.__handleClose(destroy=True)
        # Allow user to snap images
        self.snapButton.configure(state='normal')

    def __snapImage(self):
        print("Snap!")
        self.damageApp.snapImage(os.path.join(self.outputPath, self.sensorList[self.step]['sensor']))
        if self.step < len(self.sensorList) - 1:
            self.step += 1
            stepGrid(self.sensorList, self.step)

if __name__ == '__main__':
    app = BatchProcessUI()
    app.run()
