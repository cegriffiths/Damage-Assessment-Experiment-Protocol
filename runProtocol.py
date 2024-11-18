## PROTOCOL SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## Controls the electromechanical system (controls robot, stage, solenoids, and camera), 
# logs data, and has a user interface displaying relevant information.

import stage
import camera
import dataHandling
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os

import DamageInspectionRigApp as DI
from PIL import ImageTk, Image, ImageDraw

class executer:
    def __init__(self):
        self.root = Tk()
        self.root.title("Experiment Setup")

        # Attributes to store user inputs
        self.experimentFilePath = None
        self.EE = StringVar()
        self.numPnPCycles = IntVar()
        self.imagingInterval = IntVar()

        self.file_button = None

        self.initialGUI()

        self.dataManager = dataHandling.dataManager(self.experimentFilePath)
        self.dataManager.readExperimentFile()

        # print("Experiment File:", self.experimentFilePath, "\nEE:", self.EE, "\nPnP cycles:", self.numPnPCycles, "\nImaging Interval:", self.imagingInterval)
        # self.stage = stage.stage
        # self.camera = camera.camera
        # self.dataManager = dataHandling.dataManager

    def initialGUI(self):
        '''Sets up the GUI to choose the experiment file, End Effector, Number of PnP cycles, and frequency of Images'''

        # Experiment file selection
        Label(self.root, text="Choose Experiment File").grid(row=0, column=0, pady=5, padx=10)
        self.file_button = Button(self.root, text="Choose Experiment File", command=self.choose_experiment_file)
        self.file_button.grid(row=0, column=1, pady=5, padx=10)
        
        # End effector dropdown menu
        Label(self.root, text="Select End Effector").grid(row=1, column=0, pady=5, padx=10)
        EE_options = ["EE1", "EE2", "EE3"]  # Example options
        EE_menu = ttk.Combobox(self.root, textvariable=self.EE, values=EE_options)
        EE_menu.grid(row=1, column=1, pady=5, padx=10)
        EE_menu.set("Select End Effector")
        
        # Number of pick and place cycles
        Label(self.root, text="Number of Pick and Place Cycles").grid(row=2, column=0, pady=5, padx=10)
        cycles_entry = Entry(self.root, textvariable=self.numPnPCycles)
        cycles_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Image interval
        Label(self.root, text="Imaging Interval (cycles/image)").grid(row=3, column=0, pady=5, padx=10)
        interval_entry = Entry(self.root, textvariable=self.imagingInterval)
        interval_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # Submit button
        submit_button = Button(self.root, text="Submit", command=self.submit)
        submit_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.root.mainloop()

    def choose_experiment_file(self):
        '''Opens a file dialog for selecting an experiment file and displays the file name on the button'''
        self.experimentFilePath = filedialog.askopenfilename(
            title="Select Experiment File",
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )
        
        if self.experimentFilePath:
            # Display just the file name in the button text
            file_name = os.path.basename(self.experimentFilePath)
            self.file_button.config(text=file_name)
            print("Selected Experiment File:", self.experimentFilePath)

    def submit(self):
        '''Stores input values and closes the GUI'''
        print("Experiment File:", self.experimentFilePath)
        print("End Effector:", self.EE.get())
        print("Pick and Place Cycles:", self.numPnPCycles.get())
        print("Imaging Interval (cycles/image):", self.imagingInterval.get())

        self.root.destroy()

    def run(self):
        '''Runs the overall system protocol'''
        self.stage.moveto(self.stage, 10)
        self.camera.checkCalibration(self.camera)


if __name__ == '__main__':
    execute = executer()
    # execute.run()
