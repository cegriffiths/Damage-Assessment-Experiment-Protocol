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
# import robotcontrol
import os
import threading
import time
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject


class executer(QObject):

    SENSOR_POSITIONS = [
        [0.0718, -0.449, 0.1123, 0, 3.14, 0],
        [0.0718, -0.469, 0.1123, 0, 3.14, 0],
        [0.0718, -0.489, 0.1123, 0, 3.14, 0],
        [0.0718, -0.509, 0.1123, 0, 3.14, 0],
        ]

    update_state = Signal(str)  # Signal which, when the state is updated here, calls the function in MainWindow

    def __init__(self):
        super().__init__()
        self.dataHandler = dataHandling.DataManager()
        self.dataHandler.create_log()

        self.cameraApp = CA.App()
        print("PROTOCOL: Opened camera")

        self.stage = stage.stage()
        self.stage.calibrate()
        print("PROTOCOL: Calibrated stage")

        # self.robot = robotcontrol.RobotExt()
        # self.robot.calibrate()
        print("PROTOCOL: Calibrated robot")

        self.UIHandler = UIScript.MainWindow(self.stage, self.dataHandler, self.cameraApp)
        # self.stage.update_stage.connect(self.UIHandler.updateComponents)
        # self.UIHandler.updateComponents()
        self.UIHandler.flags_updated.connect(self.checkFlags)

        self.update_state.connect(self.UIHandler.updateExperimentState)
        self.state = "Initializing"
        self.change_state(self.state)

        self.UIHandler.show()

### Attempt to make UI appear before calibrating stage

    # def __init__(self):
    #     super().__init__()

    #     self.dataHandler = dataHandling.DataManager()
    #     self.cameraApp = CA.App()

    #     # Initialize UI first without objects
    #     self.UIHandler = UIScript.MainWindow(dataHandler = self.dataHandler, CameraApp = self.cameraApp)
    #     self.UIHandler.show()

    #     self.stage = stage.stage()
    #     self.stage.calibrate()

    #     # Assign objects after initialization
    #     self.UIHandler.set_stage(self.stage)
    #     # self.UIHandler.set_dataHandler(self.dataHandler)
    #     # self.UIHandler.set_cameraApp(self.cameraApp)

    #     self.UIHandler.flags_updated.connect(self.checkFlags)

    #     # self.update_state = Signal(str)
    #     self.update_state.connect(self.UIHandler.updateExperimentState)

    #     self.state = "Initializing"
    #     self.change_state(self.state)

    #     # self.UIHandler.show()

    def change_state(self, newState):
        self.state = newState
        self.update_state.emit(self.state)
        print(f"PROTOCOL: System state updated to: {self.state}")

    def checkFlags(self):
        """Check all flags when a flag is updated"""
        if self.UIHandler.dataInputsFlag and self.UIHandler.calibratedCameraFlag:
            self.change_state("Ready")
            self.dataHandler.rename_log()

    def run_protocol(self):
        """Executes the main protocol logic."""
        # Logic for protocol execution
        while self.state == "Initializing":
            time.sleep(0.5)

        print("PROTOCOL: Running protocol...")
        time.sleep(1)
        self.change_state("Running")

        # This will always start on the first row. We should change this eventually to allow for starting on any row.
        for row in range(self.dataHandler.gelpak_dimensions[0]):
            self.image_row(row = row, go_back=False)
            self.stage.moveto(347)
                        
            picks_done = 0
            while picks_done < self.dataHandler.num_pnp_cycles:
                picks_to_do = min(self.dataHandler.num_pnp_cycles - picks_done, self.dataHandler.imaging_interval)
                self.robot.run(picks_to_do, self.dataHandler.num_pnp_cycles, self.SENSOR_POSITIONS)
                picks_done += picks_to_do
                self.image_row(row = row, go_back=True)
                
            # for PnP in range(self.dataHandler.num_pnp_cycles):
            #     print(f"Run Robot through row = {row}\tPnP = {PnP}")
            #     for col in range(self.dataHandler.gelpak_dimensions[1]):
            #         sensor = self.dataHandler.get_sensor(row, col)
            #         if sensor:  # Only increment if a sensor exists
            #             self.dataHandler.increment_pnp_cycles(row, col)
            #             pnp_cycles = "PnP_cycles"
            #             self.dataHandler.log(f"PnP'd number {sensor[pnp_cycles]} of sensor at ({row}, {col})")

            #     self.dataHandler.update_experiment_file()

        ## Code for robot

        # self.robot.run(1, self.dataHandler.numPnPCycles, sensor_positions)

    def image_row(self, row, go_back=True):
        return_location = self.stage.position

        for col in range(self.dataHandler.gelpak_dimensions[1]):
            sensor = self.dataHandler.get_sensor(row, col)
            if sensor:  # Check if a sensor exists at this position
                # Map column to stage position
                stage_position = {0: 60, 1: 40, 2: 30, 3: 20}.get(col) #These need to get updated
                self.stage.moveto(stage_position)
                self.snapImage(row, col)
                self.dataHandler.increment_num_photos(row, col)
                # print(sensor["photos"])
                photos = "photos"
                print(f"PROTOCOL: Took picture number {sensor[photos]} of sensor at ({row}, {col})")
                time.sleep(1)
                self.UIHandler.updateSensorInformation()

        if go_back:
            self.stage.moveto(return_location)

    def run_protocol_in_background(self):
        protocol_thread = threading.Thread(target=self.run_protocol, daemon=True)
        protocol_thread.start()

    def snapImage(self, row, col):
        print(f"PROTOCOL: Snap! Row: {row}, Col: {col}")
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        ## Add back when we actually want images
        # self.cameraApp.snapImage(os.path.join(self.dataHandler.image_folder_path, timestamp))


if __name__ == '__main__':
    app = QApplication([])
    execute = executer()
    execute.run_protocol_in_background()
    app.exec()
