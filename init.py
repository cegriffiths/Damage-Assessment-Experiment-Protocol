## INITIALIZATION SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script allows user to select an experiment file, sensors file, reads said files, calibrates the electromechanical system 
# and puts it in its initial condition

from tkinter import messagebox
import json
import pandas as pd

class Sensors:
    def __init__(self, sensor_number, interactions):
        self.intitialize

def initialize(path):
    print("Initializing from: ", path)
    messagebox.askokcancel("Warning!", "Directory already exists for: CSV. Do you want to overwrite it?")


