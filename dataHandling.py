## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 12, 2024
# UBC ENPH 479

## This script allows the reading of experiment files, and allows writting to log files

import json
from datetime import datetime
import os

class sensor:
    def __init__(self, ID = None, PnPCycles = None, numPhotos = None):
        self.ID = ID
        self.PnPCycles = PnPCycles
        self.numPhotos = numPhotos

    def incrementPnPCycles(self):
        self.PnPCycles = self.PnPCycles + 1

    def incrementNumPhotos(self):
        self.numPhotos = self.numPhotos + 1


class dataManager:
    def __init__(self):
        self.gui_window = None
        self.experimentFilePath = None
        self.EE = None
        self.numPnPCycles = None
        self.imagingInterval = None
        self.logdir = "LOGS"
        self.GelPakID = None
        self.griddim = None
        self.sensors = [[sensor() for i in range(4)] for j in range(3)]
        # self.logFilePath

    def readExperimentFile(self):
        '''Read Experiment File, store in self object'''
        with open(self.experimentFilePath) as f:
            experimentData = json.load(f)
        # print(self.experimentData)
        # print(experimentData["grid"])

        self.GelPakID = experimentData["GelPak ID"]
        # self.sensors = experimentData["grid"]
        self.griddim = [len(experimentData["grid"]), len(experimentData["grid"][0])]    ## rows by columns
        for row in range(self.griddim[0]):
            for col in range(self.griddim[1]):
                self.sensors[row][col].ID = experimentData["grid"][row][col]["ID"]
                self.sensors[row][col].PnPCycles = experimentData["grid"][row][col]["PnP_cycles"]
                self.sensors[row][col].numPhotos = experimentData["grid"][row][col]["photos"]

        print("Read Experiment File")
        # print("GelPakID:", self.GelPakID, "\nSensors:", self.sensors, "\nGrid Dimensions:", self.griddim)
        # print(self.sensors[0][0]["location"])
        # return [self.GelPakID, self.sensors, self.griddim]

    def updateExperimentFile(self):
        '''Update the experiment file'''
        updatedData = {"GelPak ID": self.GelPakID,
                       "grid": self.sensors}
        with open(self.experimentFilePath, "w") as f:
            json.dump(updatedData, f, indent=4)

        print(f"Experiment file '{self.experimentFilePath}' updated successfully!")
        
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

## Testing Functions

# sensor = Sensors('EXPERIMENT_INPUTS/testjson.json')
# sensor.readExperimentFile()
# sensor.createlog()
# sensor.log("Succesfully Logged Data")
# sensor.log("Succesfull log #2")