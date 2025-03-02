## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 12, 2024
# UBC ENPH 479

## This script allows the reading of experiment files, and allows writting to log files

# import json
# from datetime import datetime
# import os

# class sensor:
#     def __init__(self, ID = None, PnPCycles = None, numPhotos = None):
#         self.ID = ID
#         self.PnPCycles = PnPCycles
#         self.numPhotos = numPhotos

#     def incrementPnPCycles(self):
#         self.PnPCycles = self.PnPCycles + 1

#     def incrementNumPhotos(self):
#         self.numPhotos = self.numPhotos + 1


# class dataManager:
#     def __init__(self):
#         self.gui_window = None
#         self.experimentFilePath = None
#         self.EE = None
#         self.numPnPCycles = None
#         self.imagingInterval = None
#         self.logdir = "LOGS"
#         self.imagedir = "OUTPUT_IMAGES"
#         self.GelPakID = None
#         self.griddim = None
#         self.sensors = [[sensor() for i in range(4)] for j in range(3)]
#         # self.logFilePath

#     def readExperimentFile(self):
#         '''Read Experiment File, store in self object'''
#         with open(self.experimentFilePath) as f:
#             experimentData = json.load(f)
#         # print(self.experimentData)
#         # print(experimentData["grid"])

#         self.GelPakID = experimentData["GelPak ID"]
#         # self.sensors = experimentData["grid"]
#         self.griddim = [len(experimentData["grid"]), len(experimentData["grid"][0])]    ## rows by columns
#         for row in range(self.griddim[0]):
#             for col in range(self.griddim[1]):
#                 self.sensors[row][col].ID = experimentData["grid"][row][col]["ID"]
#                 self.sensors[row][col].PnPCycles = experimentData["grid"][row][col]["PnP_cycles"]
#                 self.sensors[row][col].numPhotos = experimentData["grid"][row][col]["photos"]

#         print("Read Experiment File")
#         # print("GelPakID:", self.GelPakID, "\nSensors:", self.sensors, "\nGrid Dimensions:", self.griddim)
#         # print(self.sensors[0][0]["location"])
#         # return [self.GelPakID, self.sensors, self.griddim]

#     def updateExperimentFile(self):
#         '''Update the experiment file'''
#         updatedData = {"GelPak ID": self.GelPakID,
#                        "grid": self.sensors}
#         with open(self.experimentFilePath, "w") as f:
#             json.dump(updatedData, f, indent=4)

#         print(f"Experiment file '{self.experimentFilePath}' updated successfully!")
        
#     def createlog(self):
#         '''Create Log file'''
#         # Make directory if it doesn't already exist
#         os.makedirs(self.logdir, exist_ok=True)

#         # Get current date and time
#         time = datetime.now()
#         timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

#         # Combine directory, gelpak id and timestamp to make the relative path of the file
#         self.logFilePath = os.path.join(self.logdir, f"{self.GelPakID}_log_{timestamp}.txt")

#         # Write log file
#         with open(self.logFilePath, 'w') as file:
#             file.write(f"Log begins at {timestamp}\n")

#         # Print Statement Check
#         print(f"Log file '{self.logFilePath}' created with starting message.")
        
#     def log(self, string):
#         '''Write to log file'''

#         # Get current date and time
#         timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

#         # Append new string to log file
#         with open(self.logFilePath, 'a') as file:
#             file.write(f"[{timestamp}] {string}\n")
#         print(f"Appended '{string}' to {self.logFilePath}")

## Testing Functions

# sensor = Sensors('EXPERIMENT_INPUTS/testjson.json')
# sensor.readExperimentFile()
# sensor.createlog()
# sensor.log("Succesfully Logged Data")
# sensor.log("Succesfull log #2")





import json
from datetime import datetime
import os
import sys
import logging
from typing import List, Dict, Optional

class DataManager:
    def __init__(self):
        # Path information
        self.experiment_file_path: Optional[str] = None
        self.log_file_path: Optional[str] = None
        self.image_folder_path: str = "OUTPUT_IMAGES"
        
        # Experiment information
        self.EE: Optional[str] = None  # EE being used
        self.num_pnp_cycles: Optional[int] = None  # Number of PnP cycles to perform per sensor
        self.imaging_interval: Optional[int] = None  # Imaging interval
        self.current_row = 1
        
        # Sensor information
        self.gelpak_id: Optional[str] = None  # GelPak ID
        self.gelpak_dimensions: List[int] = [3, 4]  # Maximum GelPak dimensions (3 rows x 4 columns)
        self.sensors: List[Dict] = []  # List of sensors, each represented as a dictionary
        
        # Log directory
        self.log_dir: str = "LOGS"
        os.makedirs(self.log_dir, exist_ok=True)  # Create log directory if it doesn't exist

    def read_experiment_file(self, experiment_file_path: str, EE: str, num_pnp_cycles: int, imaging_interval:int):
        """Read the experiment file and populate the data manager."""
        self.experiment_file_path = experiment_file_path
        self.EE = EE
        self.num_pnp_cycles = num_pnp_cycles
        self.imaging_interval = imaging_interval
        with open(experiment_file_path, "r") as f:
            experiment_data = json.load(f)
        
        # Load experiment information
        self.gelpak_id = experiment_data.get("GelPak ID")
        # self.EE = experiment_data.get("EE")
        # self.num_pnp_cycles = experiment_data.get("NumPnPCycles")
        # self.imaging_interval = experiment_data.get("ImagingInterval")
        
        # Load sensor information
        self.sensors = experiment_data.get("grid", [])
        print(f"DATA: Experiment file '{experiment_file_path}' read successfully.")

    def update_experiment_file(self):
        """Update the experiment file with the current data."""
        if not self.experiment_file_path:
            raise ValueError("Experiment file path is not set.")
        
        experiment_data = {
            "GelPak ID": self.gelpak_id,
            "EE": self.EE,
            "NumPnPCycles": self.num_pnp_cycles,
            "ImagingInterval": self.imaging_interval,
            "grid": self.sensors
        }
        
        with open(self.experiment_file_path, "w") as f:
            json.dump(experiment_data, f, indent=4)
        print(f"DATA: Experiment file '{self.experiment_file_path}' updated successfully.")

    def create_log(self):
        """Create a log file for the experiment."""
        # if not self.gelpak_id:
        #     raise ValueError("GelPak ID is not set.")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.gelpak_id}_log_{timestamp}.txt" if self.gelpak_id else f"unnamed_log_{timestamp}.txt"

        self.log_file_path = os.path.join(self.log_dir, filename)
        
        logging.basicConfig(filename=self.log_file_path, level=logging.INFO, format="[%(asctime)s] %(message)s")
        sys.stdout = self
        sys.stderr = self

        print(f"DATA: Log file '{self.log_file_path}' created successfully.")
    
    def rename_log(self):
        """Rename log file when GelPak ID becomes available."""
        print(f"DATA: Renaming Log File with GelPak: {self.gelpak_id}")
        if not self.gelpak_id or not self.log_file_path:
            return  # No need to rename if there's no GelPak ID or log file

        new_filename = f"{self.gelpak_id}_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        new_path = os.path.join(self.log_dir, new_filename)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        logging.shutdown()  # Force close all log files and handlers

        # **Remove all existing logging handlers**
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        try:
            os.rename(self.log_file_path, new_path)

            sys.stdout = self
            sys.stderr = self

            # Reconfigure logging to use the new file
            logging.basicConfig(filename=new_path, level=logging.INFO, format="[%(asctime)s] %(message)s")

            print(f"DATA: Log file renamed from '{self.log_file_path}' to '{new_path}'")
            self.log_file_path = new_path  # Update reference

        except OSError as e:
            print(f"DATA: Failed to rename log file: {e}")

    def log(self, message: str):
        """Append a message to the log file."""
        if not self.log_file_path:
            raise ValueError("Log file path is not set.")
        
        # timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
        # with open(self.log_file_path, "a") as file:
        #     file.write(f"[{timestamp}] {message}\n")
        # print(f"Appended '{message}' to log file.")

        logging.info(message)
        sys.__stdout__.write(message + '\n')
        sys.__stdout__.flush()

    def write(self, message: str):
        """Overwrite function for stdout/stderr redirection"""
        if message.strip():
            self.log(message)

    def flush(self):
        """Needed for compatibility with sdtout redirection"""
        pass

    def get_sensor(self, row: int, col: int) -> Optional[Dict]:
        """Get sensor information by row and column."""
        for sensor in self.sensors:
            if sensor["row"] == row and sensor["col"] == col:
                return sensor
        return None

    def increment_pnp_cycles(self, row: int, col: int):
        """Increment the PnP cycles for a sensor."""
        sensor = self.get_sensor(row, col)
        if sensor:
            sensor["PnP_cycles"] += 1
            print(f"DATA: Incremented PnP cycles for sensor at row {row}, col {col}.")
        else:
            print(f"DATA: No sensor found at row {row}, col {col}.")

    def increment_num_photos(self, row: int, col: int):
        """Increment the number of photos for a sensor."""
        sensor = self.get_sensor(row, col)
        if sensor:
            sensor["photos"] += 1
            print(f"DATA: Incremented photos for sensor at row {row}, col {col}.")
        else:
            print(f"DATA: No sensor found at row {row}, col {col}.")

    def add_sensor(self, sensor_id: str, row: int, col: int, pnp_cycles: int = 0, photos: int = 0):
        """Add a new sensor to the grid."""
        if row >= self.gelpak_dimensions[0] or col >= self.gelpak_dimensions[1]:
            raise ValueError("Sensor position is outside GelPak dimensions.")
        
        sensor = {
            "ID": sensor_id,
            "row": row,
            "col": col,
            "PnP_cycles": pnp_cycles,
            "photos": photos
        }
        self.sensors.append(sensor)
        print(f"DATA: Added sensor '{sensor_id}' at row {row}, col {col}.")

    def get_gelpak_dimensions(self) -> List[int]:
        """Get the dimensions of the GelPak."""
        return self.gelpak_dimensions
    
    def increment_row(self):
        """Increment the current row"""
        self.current_row = self.current_row + 1
        print(f"DATA: Current row updated to {self.current_row}")