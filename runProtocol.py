## PROTOCOL SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## Controls the electromechanical system (controls robot, stage, solenoids, and camera), 
# logs data, and has a user interface displaying relevant information.

import stage
import camera
import dataHandling
import UIScript
import os
from PySide6.QtWidgets import QApplication

import DamageInspectionRigApp as DI
from PIL import ImageTk, Image, ImageDraw

class executer:
    def __init__(self):
        self.UIHandler = UIScript.MainWindow()
        self.UIHandler.show()
        self.dataHandler = dataHandling.dataManager()

    def start_experiment_setup(self):
        """Initializes the data handling and shows the first UI."""
        

        # Proceed to the next step
        # self.start_stage_setup()

    def start_stage_setup(self):
        """Initializes the stage and runs its calibration."""
        self.stage = stage.stage()

        # Move on to initialize Robot
        # self.start_robot_setup()

    def start_robot_setup(self):
        """Initialize the robot and get to starting position"""
        ## To-Do

        # self.start_camera_setup()
    
    def start_camera_setup(self):
        """Initializes the camera and opens the calibration UI."""
        # self.camera.run()

        # # Proceed to the next step
        # self.start_main_ui()

    def start_main_ui(self):
        """Displays the main UI for monitoring protocol execution."""
        # Call the main run function
        self.run_protocol()

    def run_protocol(self):
        """Executes the main protocol logic."""
        # Logic for protocol execution
        print("Running protocol...")


if __name__ == '__main__':
    app = QApplication([])
    execute = executer()
    app.exec()
