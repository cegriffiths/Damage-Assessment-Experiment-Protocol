## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 12, 2024
# UBC ENPH 479

## This script allows the reading of experiment files, and allows writting to log files

from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import json
import pandas as pd
from datetime import datetime
import os

class dataManager:
    def __init__(self, root = Tk()):
        self.root = root
        self.gui_window = None
        self.experimentFilePath = None
        self.EE = StringVar()
        self.numPnPCycles = IntVar()
        self.imagingInterval = IntVar()
        self.logdir = "LOGS"
        # self.logFilePath


    def readExperimentFile(self):
        '''Read Experiment File, store in self object'''
        with open(self.experimentFilePath) as f:
            experimentData = json.load(f)
        # print(self.experimentData)
        # print(experimentData["grid"])

        self.GelPakID = experimentData["GelPak ID"]
        self.sensors = experimentData["grid"]
        self.griddim = [len(experimentData["grid"]), len(experimentData["grid"][0])]

        print("GelPakID:", self.GelPakID, "\nSensors:", self.sensors, "\nGrid Dimensions:", self.griddim)
        # print(self.sensors[0][0]["location"])
        # return [self.GelPakID, self.sensors, self.griddim]

    def updateExperimentFile(self):
        '''Update the experiment file'''
        
    def createlog(self):
        '''Create Log file'''
        # Make directory if it doesn't already exist
        os.makedirs(self.logdir, exist_ok=True)

        # Get current date and time
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

        # Combine directory, gelpak id and timestamp to make the relative path of the file
        self.logFilePath = os.path.join(self.logdir, f"{self.GelPakID}_log_{timestamp}.txt")

        # Write log file
        with open(self.logFilePath, 'w') as file:
            file.write(f"Log begins at {timestamp}\n")

        # Print Statement Check
        print(f"Log file '{self.logFilePath}' created with starting message.")
        
    def log(self, string):
        '''Write to log file'''

        # Get current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

        # Append new string to log file
        with open(self.logFilePath, 'a') as file:
            file.write(f"[{timestamp}] {string}\n")
        print(f"Appended '{string}' to {self.logFilePath}")

    def initialGUI(self):
        '''Sets up the GUI to choose the experiment file, End Effector, Number of PnP cycles, and frequency of Images'''
        # Create toplevel from root
        self.gui_window = Toplevel(self.root)
        self.gui_window.title("Experiment Setup")
        self.gui_window.grab_set()  # Makes the window modal so blocks interaction with other windows

        # Experiment file selection
        Label(self.gui_window, text="Choose Experiment File").grid(row=0, column=0, pady=5, padx=10)
        self.file_button = Button(self.gui_window, text="Choose Experiment File", command=self.choose_experiment_file)
        self.file_button.grid(row=0, column=1, pady=5, padx=10)
        
        # End effector dropdown menu
        Label(self.gui_window, text="Select End Effector").grid(row=1, column=0, pady=5, padx=10)
        EE_options = ["Circular Planar", "Rectangular Planar"]  # Example options
        EE_menu = ttk.Combobox(self.gui_window, textvariable=self.EE, values=EE_options)
        EE_menu.grid(row=1, column=1, pady=5, padx=10)
        EE_menu.set("Select End Effector")
        
        # Number of pick and place cycles
        Label(self.gui_window, text="Number of Pick and Place Cycles").grid(row=2, column=0, pady=5, padx=10)
        cycles_entry = Entry(self.gui_window, textvariable=self.numPnPCycles)
        cycles_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Image interval
        Label(self.gui_window, text="Imaging Interval (cycles/image)").grid(row=3, column=0, pady=5, padx=10)
        interval_entry = Entry(self.gui_window, textvariable=self.imagingInterval)
        interval_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # Submit button
        submit_button = Button(self.gui_window, text="Submit", command=self.submit)
        submit_button.grid(row=4, column=0, columnspan=2, pady=10)

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

        self.gui_window.destroy()

## Testing Functions

# sensor = Sensors('EXPERIMENT_INPUTS/testjson.json')
# sensor.readExperimentFile()
# sensor.createlog()
# sensor.log("Succesfully Logged Data")
# sensor.log("Succesfull log #2")