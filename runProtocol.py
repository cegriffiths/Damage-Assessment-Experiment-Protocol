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
from PySide6.QtWidgets import QApplication

class executer:
    def __init__(self):
        self.dataHandler = dataHandling.dataManager()
        self.cameraApp = CA.App()
        self.stage = stage.stage()
        self.stage.calibrate()
        self.UIHandler = UIScript.MainWindow(self.dataHandler, self.cameraApp)
        self.UIHandler.show()

    def run_protocol(self):
        """Executes the main protocol logic."""
        # Logic for protocol execution
        print("Running protocol...")
        self.stage.moveto(10)

    def run_protocol_in_background(self):
        protocol_thread = threading.Thread(target=self.run_protocol, daemon=True)
        protocol_thread.start()


if __name__ == '__main__':
    app = QApplication([])
    execute = executer()
    app.exec()
    execute.run_protocol_in_background()
