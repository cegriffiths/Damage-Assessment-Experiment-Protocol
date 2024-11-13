## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 12, 2024
# UBC ENPH 479

## This script allows the reading of experiment files, and allows writting to log files

from tkinter import messagebox
import json
import pandas as pd
from datetime import datetime
import os

class Sensors:
    def __init__(self, expfilepath):
        self.expfilepath = expfilepath
        self.logdir = "LOGS"
        # self.logfilepath

    def readExperimentFile(self):
        '''Read Experiment File, store in self object'''
        with open(self.expfilepath) as f:
            expdata = json.load(f)
        # print(self.expdata)
        # print(expdata["grid"])

        self.GelPakID = expdata["GelPak ID"]
        self.sensors = expdata["grid"]
        self.griddim = [len(expdata["grid"]), len(expdata["grid"][0])]

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
        self.logfilepath = os.path.join(self.logdir, f"{self.GelPakID}_log_{timestamp}.txt")

        # Write log file
        with open(self.logfilepath, 'w') as file:
            file.write(f"Log begins at {timestamp}\n")

        # Print Statement Check
        print(f"Log file '{self.logfilepath}' created with starting message.")
        
    def log(self, string):
        '''Write to log file'''

        # Get current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

        # Append new string to log file
        with open(self.logfilepath, 'a') as file:
            file.write(f"[{timestamp}] {string}\n")
        print(f"Appended '{string}' to {self.logfilepath}")

## Testing Functions

# sensor = Sensors('EXPERIMENT_INPUTS/testjson.json')
# sensor.readExperimentFile()
# sensor.createlog()
# sensor.log("Succesfully Logged Data")
# sensor.log("Succesfull log #2")