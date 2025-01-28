## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 22, 2024
# UBC ENPH 479

## This script will host all of the UIs, including interfacing with the dataHandler, Camera, and general states from runProtocol.

import os
import sys
import dataHandling
import CameraApp as CA
import stage
import amcam
from datetime import datetime
import PySide6
from PySide6.QtCore import QDate, QDir, QStandardPaths, Qt, QUrl, Slot, Signal, QObject
from PySide6.QtGui import QAction, QGuiApplication, QDesktopServices, QIcon
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QTabWidget, QToolBar, QVBoxLayout, QWidget,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox, QCheckBox, QGridLayout)
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices)
from PySide6.QtMultimediaWidgets import QVideoWidget

# Set the QT_PLUGIN_PATH to the platforms folder
os.environ["QT_PLUGIN_PATH"] = os.path.join(os.path.dirname(PySide6.__file__), "plugins")

class SensorLayout(QWidget):
    def __init__(self, sensorPos, sensorID, numPnP):
        super().__init__()
        self.sensor_Pos = sensorPos
        self.sensor_id = sensorID
        self.cycles = numPnP
        
        # Layout for each sensor
        layout = QVBoxLayout()
        
        # Labels for ID and cycles
        # self.pos_label = QLabel(f"Position: {self.sensor_Pos}")
        self.id_label = QLabel(f"Sensor ID: {self.sensor_id}")
        self.cycles_label = QLabel(f"Cycles: {self.cycles}")
        
        # Add labels to layout
        layout.addWidget(self.id_label)
        layout.addWidget(self.cycles_label)
        
        self.setLayout(layout)
    
    def updateID(self, ID):
        self.sensor_id = ID
        self.id_label.setText(f"Sensor ID: {self.sensor_id}")

    def updateCycles(self, cycles):
        self.cycles = cycles
        self.cycles_label.setText(f"Cycles: {self.cycles}")

class MainWindow(QMainWindow):

    flags_updated = Signal()    ## Signal which

    def __init__(stage, self, dataHandler = dataHandling.dataManager(), CameraApp = CA.App()):
    # def __init__(self, dataHandler = dataHandling.dataManager(), CameraApp = CA.App()):
        super().__init__()
        self.dataHandler = dataHandler
        self.CameraApp = CameraApp
        self.stage = stage
        self.CameraApp.setLiveCallback(self.liveCallback)
        self.outputPath = "OUTPUT_IMAGES"
        ## Flags
        self.dataInputsFlag = False         # Flag to check that we have experimental inputs
        self.calibratedCameraFlag = False   # Flag to check that the camera is calibrated

        self.initUI()
        self.CameraApp.run()

    def initUI(self):
        self.setWindowTitle("Experiment Setup")

        # Main layout container
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        title_font = QFont("Arial", 20, QFont.Bold)
        header_font = QFont("Arial", 16, QFont.Bold)


        ## Main State
        self.experiment_state_label = QLabel("State: ")
        self.experiment_state_label.setFont(title_font)
        main_layout.addWidget(self.experiment_state_label, alignment=Qt.AlignCenter)
        # main_layout.addWidget(self.experiment_state_label)


        ## System Information (experiment inputs, sensor information, stage information, robot information, camera information)
        sys_information_layout = QHBoxLayout()


        ## Stage, Robot, Sensors and Experimental Inputs
        left_layout = QVBoxLayout()


        ## Robot and Stage Information
        robot_stage_layout = QHBoxLayout()

        # Stage Information
        stage_layout = QVBoxLayout()
        self.stage_label = QLabel("Stage Information")
        self.stage_label.setFont(header_font)
        self.stage_state_label = QLabel("State: ")
        self.stage_currentPos_label = QLabel("Current Position: ")
        # self.stage_desiredPos_label = QLabel("Desired Position: ")
        stage_layout.addWidget(self.stage_label, alignment=Qt.AlignHCenter)
        stage_layout.addWidget(self.stage_state_label)
        stage_layout.addWidget(self.stage_currentPos_label)
        # stage_layout.addWidget(self.stage_desiredPos_label)
        robot_stage_layout.addLayout(stage_layout)
        # robot_stage_layout.addWidget(stage_container)

        # Robot Information
        robot_layout = QVBoxLayout()
        robot_layout.setSpacing(5)
        robot_layout.setContentsMargins(0, 0, 0, 0)
        self.robot_label = QLabel("Robot Information")
        self.robot_label.setFont(header_font)
        self.robot_state_label = QLabel("State: ")
        robot_layout.addWidget(self.robot_label, alignment=Qt.AlignHCenter)
        robot_layout.addWidget(self.robot_state_label)
        robot_stage_layout.addLayout(robot_layout)

        left_layout.addLayout(robot_stage_layout)


        # Sensor Information
        sensor_layout = QVBoxLayout()
        self.sensor_label = QLabel("Sensor Information")
        self.sensor_label.setFont(header_font)
        self.sensor_grid_layout = QGridLayout()
        for row in range(3):
            for col in range(4):
                sensorPos = [row, col]
                sensorID = self.dataHandler.sensors[row][col].ID
                numPnP = self.dataHandler.sensors[row][col].PnPCycles
                sensorWidget = SensorLayout(sensorPos, sensorID, numPnP)
                self.sensor_grid_layout.addWidget(sensorWidget, row, col)
        
        sensor_layout.addWidget(self.sensor_label, alignment=Qt.AlignHCenter)
        sensor_layout.addLayout(self.sensor_grid_layout)
        left_layout.addLayout(sensor_layout)
        
        # Experiment Setup
        experiment_layout = QVBoxLayout()
        self.experiment_label = QLabel("Experiement Setup")
        self.experiment_label.setFont(header_font)
        experiment_layout.addWidget(self.experiment_label, alignment=Qt.AlignHCenter)
        # Experiment File Selection Dropdown
        file_layout = QHBoxLayout()
        file_label = QLabel("Select File:")
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("No file selected")
        self.file_input.setReadOnly(True)  # Make the file path non-editable
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.file_button)
        experiment_layout.addLayout(file_layout)
        # EE selection Menu
        EE_dropdown_layout = QHBoxLayout()
        EE_dropdown_label = QLabel("Options:")
        self.EE_dropdown = QComboBox()
        self.EE_dropdown.addItems(["Circular Planar", "Rectangular Planar"])
        EE_dropdown_layout.addWidget(EE_dropdown_label)
        EE_dropdown_layout.addWidget(self.EE_dropdown)
        experiment_layout.addLayout(EE_dropdown_layout)
        # Number of PnP cycles per sensor input
        PnP_cycles_layout = QHBoxLayout()
        PnP_cycles_label = QLabel("Number of Pick and Place Cycles:")
        self.PnP_cycles_input = QSpinBox()
        self.PnP_cycles_input.setRange(0, 100)  # Set the range for the number input
        self.PnP_cycles_input.setValue(50)  # Default value
        PnP_cycles_layout.addWidget(PnP_cycles_label)
        PnP_cycles_layout.addWidget(self.PnP_cycles_input)
        experiment_layout.addLayout(PnP_cycles_layout)
        # Imaging Interval input
        Imaging_Interval_layout = QHBoxLayout()
        Imaging_Interval_label = QLabel("Imaging Interval (cycles/image):")
        self.Imaging_Interval_input = QSpinBox()
        self.Imaging_Interval_input.setRange(0, 100)
        self.Imaging_Interval_input.setValue(5)
        Imaging_Interval_layout.addWidget(Imaging_Interval_label)
        Imaging_Interval_layout.addWidget(self.Imaging_Interval_input)
        experiment_layout.addLayout(Imaging_Interval_layout)
        # Submit Button
        self.Submit_button = QPushButton("Submit")
        self.Submit_button.clicked.connect(self.submit_data)
        experiment_layout.addWidget(self.Submit_button)
        
        left_layout.addLayout(experiment_layout)
        
        sys_information_layout.addLayout(left_layout)

        ## Imaging Section
        imaging_layout = QVBoxLayout()
        self.imaging_label = QLabel("Imaging")
        self.imaging_label.setFont(header_font)
        imaging_layout.addWidget(self.imaging_label, alignment=Qt.AlignHCenter)
        # Livefeed
        self.livefeel_label = QLabel(self)
        self.livefeel_label.setScaledContents(True)
        imaging_layout.addWidget(self.livefeel_label)
        # Brightness Value and Sensor Area
        assessment_layout = QHBoxLayout()
        self.brightness_label = QLabel("") ## Needs to be implemented
        self.area_label = QLabel("")
        assessment_layout.addWidget(self.brightness_label)
        assessment_layout.addWidget(self.area_label)
        imaging_layout.addLayout(assessment_layout)
        # Snap, Check Calibration, and Confirm Calibration Buttons
        imaging_buttons_layout = QHBoxLayout()
        self.snap_push_button = QPushButton("Snap Image")
        self.snap_push_button.clicked.connect(self.snapImage)
        imaging_buttons_layout.addWidget(self.snap_push_button)
        self.cam_calib_push_button = QPushButton("Check Calibration")
        self.cam_calib_push_button.clicked.connect(self.checkCameraCalibration)
        imaging_buttons_layout.addWidget(self.cam_calib_push_button)
        self.confirm_calib_push_button = QPushButton("Camera is calibrated")
        self.confirm_calib_push_button.clicked.connect(self.confirmCameraCalibration)
        imaging_buttons_layout.addWidget(self.confirm_calib_push_button)
        imaging_layout.addLayout(imaging_buttons_layout)

        sys_information_layout.addLayout(imaging_layout)

        main_layout.addLayout(sys_information_layout)

        # Set main layout and widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def browse_file(self):
        # Open a file dialog and set the selected file path to the input field
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "EXPERIMENT_INPUTS", "JSON Files (*.json);;All Files (*.*)")
        if file_path:
            self.file_input.setText(file_path)

    def submit_data(self):
        self.experiment_file_path = self.file_input.text()
        self.EE = self.EE_dropdown.currentText()
        self.num_PnP_cycles = self.PnP_cycles_input.value()
        self.imaging_interval = self.Imaging_Interval_input.value()

        if not self.experiment_file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file")
            return
        
        if self.num_PnP_cycles < self.imaging_interval:
            QMessageBox.warning(self, "Input Error", "Imaging interval must be less than the number of PnP cycles")
            return
        
        self.Submit_button.setEnabled(False)
        self.file_button.setEnabled(False)
        self.EE_dropdown.setEnabled(False)
        self.PnP_cycles_input.setEnabled(False)
        self.Imaging_Interval_input.setEnabled(False)
        print(f"Experiement File: ", self.experiment_file_path, "\nEnd Effector: ", self.EE, "\nPnP Cycles: ",self.num_PnP_cycles, "\nImaging Interval: ", self.imaging_interval)
        self.dataHandler.experimentFilePath = self.experiment_file_path
        self.dataHandler.EE = self.EE
        self.dataHandler.numPnPCycles = self.num_PnP_cycles
        self.dataHandler.imagingInterval = self.imaging_interval
        self.dataInputsFlag = True  #Update Flag
        self.flags_updated.emit()   #Send Signal to executer
        self.dataHandler.readExperimentFile()
        self.updateSensorInformation()

    def updateSensorInformation(self):
        self.sensor_grid_layout
        for row in range(self.dataHandler.griddim[0]):
            for col in range(self.dataHandler.griddim[1]):
                sensorWidget = self.sensor_grid_layout.itemAtPosition(row, col).widget()
                if sensorWidget:
                    sensor = self.dataHandler.sensors[row][col]
                    sensorWidget.updateID(sensor.ID)
                    sensorWidget.updateCycles(sensor.PnPCycles)
        print("Updated Sensors in UI")

    def liveCallback(self):
        img = QImage(self.CameraApp.buf, self.CameraApp.width, self.CameraApp.height, (self.CameraApp.width * 24 + 31) // 32 * 4, QImage.Format_RGB888)
        img = img.mirrored(horizontally=False, vertically=True)
        self.livefeel_label.setPixmap(QPixmap.fromImage(img))
        if self.CameraApp.calibrating:
            self.brightness_label.setText(f"Brightness: {self.CameraApp.brightness}\tDesired Brightness: 202")
            self.area_label.setText(f"Area: {self.CameraApp.area}\tDesired Area: {376*524}")
        else:
            self.brightness_label.setText("Brightness: Not Calibrating")
            self.area_label.setText("Area: Not Calibrating")

    def closeEvent(self, event):
        self.CameraApp.closeCam()

    def snapImage(self):
        print("Snap!")
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.CameraApp.snapImage(os.path.join(self.outputPath, timestamp))

    def checkCameraCalibration(self):
        self.CameraApp.calibrating = not self.CameraApp.calibrating
        if self.CameraApp.calibrating:
            self.cam_calib_push_button.setText("Stop Calibrating")
        else:
            self.cam_calib_push_button.setText("Start Calibrating")

    def confirmCameraCalibration(self):
        self.calibratedCameraFlag = True
        self.flags_updated.emit()
        self.confirm_calib_push_button.setEnabled(False)

    def updateExperimentState(self, state):
        self.experiment_state_label.setText(f"State: {state}")

    def updateComponents(self):
        print("updating")
        # Uncomment when stage is working
        if self.stage.motionFlag == True and self.stage.manualStopFlag == False:
            self.stage_state_label = QLabel("State: Moving")
        elif self.stage.motionFlag == False and self.stage.manualStopFlag == True:
            self.stage_state_label = QLabel("State: Manual Stop")
        elif self.stage.motionFlag == False and self.stage.manualStopFlag == False:
            self.stage_state_label = QLabel("State: In Position")
        else:
            self.stage_state_label = QLabel("State: Unknown")

        self.stage_currentPos_label = QLabel(f"Current Position: {self.stage.position}")

        # self.robot_state_label = QLabel(f"State: {self.robot.state}")



# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()