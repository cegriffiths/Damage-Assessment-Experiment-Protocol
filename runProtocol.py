## PROTOCOL SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## Controls the electromechanical system (controls robot, stage, solenoids, and camera), 
# logs data, and has a user interface displaying relevant information.

import init
import robot
import stage
import camera
from tkinter import *

import DamageInspectionRigApp as DI
from PIL import ImageTk, Image, ImageDraw

class executer:
    def __init__(self):
        self.stage = stage.stage
        # self.robot = robot.robot
        self.camera = camera.camera
        self.root = Tk()
        self.state = "INIT"

    def run(self):
        '''Runs the overall system protocol'''
        init.initialize(".\\adskfjbdsa\\flijsa.py")
        self.stage.moveto(self.stage, 10)
        self.camera.checkCalibration(self.camera)


if __name__ == '__main__':
    execute = executer()
    execute.run()
