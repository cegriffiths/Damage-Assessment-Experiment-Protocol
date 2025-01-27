## PROTOCOL SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## Controls the electromechanical system (controls robot, stage, solenoids, and camera), 
# logs data, and has a user interface displaying relevant information.

import stage
import CameraApp as CA
import dataHandling
import UIScript
import os
import threading
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject

class executer(QObject):

    update_state = Signal(str)  # Signal which, when the state is updated here, calls the function in MainWindow

    def __init__(self):
        super().__init__()
        self.dataHandler = dataHandling.dataManager()

        self.cameraApp = CA.App()

        # self.stage = stage.stage()
        # self.stage.calibrate()

        # self.UIHandler = UIScript.MainWindow(self.stage, self.dataHandler, self.cameraApp)
        # self.stage.update_stage.connect(self.UIHandler.updateComponents)
        self.UIHandler = UIScript.MainWindow(self.dataHandler, self.cameraApp)
        self.UIHandler.updateComponents()
        self.UIHandler.flags_updated.connect(self.checkFlags)

        self.update_state.connect(self.UIHandler.updateExperimentState)
        self.state = "Initializing"
        self.change_state(self.state)

        self.UIHandler.show()

    def change_state(self, newState):
        self.state = newState
        self.update_state.emit(self.state)

    def checkFlags(self):
        """Check all flags when a flag is updated"""
        if self.UIHandler.dataInputsFlag and self.UIHandler.calibratedCameraFlag:
            self.change_state("Running")

    def run_protocol(self):
        """Executes the main protocol logic."""
        # Logic for protocol execution
        while self.state == "Initializing":
            time.sleep(0.5)

        print("Running protocol...")
        time.sleep(1)
        self.change_state("Running")
        # self.stage.moveto(10)

    def run_protocol_in_background(self):
        protocol_thread = threading.Thread(target=self.run_protocol, daemon=True)
        protocol_thread.start()


if __name__ == '__main__':
    app = QApplication([])
    execute = executer()
    execute.run_protocol_in_background()
    app.exec()
