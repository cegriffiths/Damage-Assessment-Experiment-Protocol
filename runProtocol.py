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
from tkinter import messagebox
import os

import DamageInspectionRigApp as DI
from PIL import ImageTk, Image, ImageDraw

class executer:
    def __init__(self, tk):
        # self.root = Tk()
        self.root = tk
        # self.root.title("Protocol Execution")
        # self.dataManager = dataHandling.dataManager(self.root)
        self.camera = camera.camera(self.root)
        # self.stage = None

    def start_experiment_setup(self):
        """Initializes the data handling and shows the first UI."""
        self.dataManager.initialGUI()
        self.root.wait_window(self.dataManager.gui_window)  # Wait for user to complete input
        
        # Proceed to the next step
        self.start_stage_setup()

    def start_stage_setup(self):
        """Initializes the stage and runs its calibration."""
        self.stage = stage.stage()
        # self.stage.calibrate()  # Placeholder for stage calibration logic
        # messagebox.showinfo("Stage Calibration", "Stage calibration completed.")  # Inform the user

        # # Proceed to the main protocol UI
        # self.start_main_ui()
        # Proceed to robot setup
        self.start_robot_setup()

    def start_robot_setup(self):
        """Initialize the robot and get to starting position"""
        ## To-Do

        self.start_camera_setup()
    
    def start_camera_setup(self):
        """Initializes the camera and opens the calibration UI."""
        # self.camera = camera.camera(self.root)
        self.camera.run()
        # self.camera.calibrationGUI()  # Assume this shows a calibration UI
        # self.camera.damageApp.run(self.root.mainloop)
        # self.camera.run()

        self.root.wait_window(self.camera.calibration_window)  # Wait for calibration completion

        # # Proceed to the next step
        # self.start_stage_setup()
        # Proceed to main ui 
        self.start_main_ui()


    def start_main_ui(self):
        """Displays the main UI for monitoring protocol execution."""
        main_ui = Toplevel(self.root)
        main_ui.title("Protocol Monitoring")
        ttk.Label(main_ui, text="Protocol is running...").pack(pady=10)

        # Call the main run function
        self.run_protocol()

    def run_protocol(self):
        """Executes the main protocol logic."""
        # Logic for protocol execution
        print("Running protocol...")
        # self.stage.moveto(10)  # Example action
        if self.camera:
            self.camera.checkCalibration()

    def run(self):
        # self.start_experiment_setup()
        self.start_camera_setup()
        # self.root.mainloop()


if __name__ == '__main__':
    tk = Tk()
    execute = executer(tk)
    execute.run()
