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
import robotcontrol
import os
import threading
import time
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject
import atexit
import signal
import sys

class executer(QObject):

    # SENSOR_POSITIONS = [
    #     [0.0698, -0.450, 0.112, 0, 3.14, 0],
    #     [0.0698, -0.467, 0.112, 0, 3.14, 0],
    #     [0.0698, -0.484, 0.112, 0, 3.14, 0],
    #     [0.0698, -0.501, 0.112, 0, 3.14, 0],
    #     ]

    SENSOR_POSITIONS = [
        [0.0698, -0.4965, 0.1115, 0, 3.14, 0],
        [0.0698, -0.5132, 0.1116, 0, 3.14, 0],
        [0.0698, -0.5300, 0.1117, 0, 3.14, 0],
        [0.0698, -0.5470, 0.1117, 0, 3.14, 0],
        ]
    
    IMAGING_STAGE_POSITIONS = {
        3: 74,
        2: 57,
        1: 40,
        0: 23,
    }

    ROBOT_STAGE_POSITION = 300
    ROW_CHANGE_STAGE_POSITION = 175

    update_state = Signal(str)  # Signal which, when the state is updated here, calls the function in MainWindow

    def __init__(self):
        super().__init__()
        self.dataHandler = dataHandling.DataManager()
        self.dataHandler.create_log()

        self.cameraApp = CA.App()
        print("PROTOCOL: Opened camera")

        self.robot = robotcontrol.RobotExt()
        self.robot.calibrate()
        print("PROTOCOL: Calibrated robot")

        self.stage = stage.stage()
        self.stage.calibrate()
        print("PROTOCOL: Calibrated stage")
        self.stage.moveto(self.IMAGING_STAGE_POSITIONS[0])

        self.UIHandler = UIScript.MainWindow(self.stage, self.dataHandler, self.cameraApp)
        # self.stage.update_stage.connect(self.UIHandler.updateComponents)
        # self.UIHandler.updateComponents()
        self.UIHandler.flags_updated.connect(self.checkFlags)
        self.stage.shutdown_signal.connect(self.UIHandler.shutdown)
        self.dataHandler.info_updated.connect(self.UIHandler.updateSensorInformation)
        self.robot.robot_state_changed.connect(self.UIHandler.on_robot_update)
        self.update_state.connect(self.UIHandler.updateExperimentState)

        self.state = "Initializing"
        self.change_state(self.state)

        self.UIHandler.show()

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
        done = False

        while not done:
            self.robot.register_callback(lambda col: self.dataHandler.increment_pnp_cycles(self.dataHandler.current_row, col))
            self.change_state("Initial Imaging")
            self.image_row(row = self.dataHandler.current_row, go_back=False)
            self.change_state("Moving to Robot")
            self.stage.moveto(self.ROBOT_STAGE_POSITION)
                        
            picks_done = 0
            while picks_done < self.dataHandler.num_pnp_cycles:
                picks_to_do = min(self.dataHandler.num_pnp_cycles - picks_done, self.dataHandler.imaging_interval)
                self.change_state("Picking Sensors")
                self.robot.run(len(self.SENSOR_POSITIONS), picks_to_do, self.SENSOR_POSITIONS)
                picks_done += picks_to_do
                self.change_state("Imaging Sensors")
                self.image_row(row = self.dataHandler.current_row, go_back=picks_done < self.dataHandler.num_pnp_cycles)
                
            self.stage.moveto(self.ROW_CHANGE_STAGE_POSITION)
            if self.dataHandler.current_row < self.dataHandler.gelpak_dimensions[0] - 1:
                self.change_state("Row Change Pause")
                self.UIHandler.row_change_dialog()
            else:
                done = True
                print("PROTOCOL: Protocol complete")
                self.change_state("Complete")

    def image_row(self, row, go_back=True):
        self.change_state("Imaging Sensors")
        return_location = self.stage.position

        for col in range(self.dataHandler.gelpak_dimensions[1]):
            sensor = self.dataHandler.get_sensor(row, col)
            if sensor:  # Check if a sensor exists at this position
                stage_position = self.IMAGING_STAGE_POSITIONS[col]
                self.stage.moveto(stage_position)
                photos = sensor["photos"]
                if self.snapImage(sensor["ID"], sensor["PnP_cycles"], photos + 1,row, col):
                    self.dataHandler.increment_num_photos(row, col)
                    print(f"PROTOCOL: Took picture number {photos} of sensor at ({row}, {col})")
                    time.sleep(1)
                    self.UIHandler.updateSensorInformation()
                else:
                    print("PROTOCOL: Error taking photo")
                    sys.exit()

        if go_back:
            self.stage.moveto(return_location)

    def run_protocol_in_background(self):
        protocol_thread = threading.Thread(target=self.run_protocol, daemon=True)
        protocol_thread.start()

    def snapImage(self, ID, num_pnp, photo, row, col):
        '''Takes image of current sensor. Returns true if taken and false if there was an error '''  
        EE = self.dataHandler.EE[:4]
        print(f"PROTOCOL: Snap! Sensor: {ID}, Row: {row}, Col: {col}, PnP: {num_pnp}, Photos: {photo}, EE: {EE}")
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return self.cameraApp.snapImage(os.path.join(self.dataHandler.image_folder_path, f"EE{EE}-ID{ID}-PNP{num_pnp}-PHOTO{photo}-T{timestamp}"))

def handle_exit():
    execute.robot.stop()
    execute.dataHandler.update_experiment_file()
    print("PROTOCOL: Saved Experiment File before closing")

def setup_exit_handlers():
    """Setup both atexit and signal handlers"""
    atexit.register(handle_exit)
    signal.signal(signal.SIGTERM, lambda signum, frame: handle_exit())
    signal.signal(signal.SIGINT, lambda signum, frame: handle_exit())


if __name__ == '__main__':
    app = QApplication([])
    execute = executer()
    setup_exit_handlers()
    execute.run_protocol_in_background()
    app.exec()
