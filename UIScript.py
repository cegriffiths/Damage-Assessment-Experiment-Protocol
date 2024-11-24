## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 22, 2024
# UBC ENPH 479

## This script will host all of the UIs, including interfacing with the dataHandler, Camera, and general states from runProtocol.

import os
import sys
import dataHandling
import CameraApp as CA
import amcam
from datetime import datetime
from PySide6.QtCore import QDate, QDir, QStandardPaths, Qt, QUrl, Slot, Signal
from PySide6.QtGui import QAction, QGuiApplication, QDesktopServices, QIcon
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QTabWidget, QToolBar, QVBoxLayout, QWidget,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox, QCheckBox)
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices)
from PySide6.QtMultimediaWidgets import QVideoWidget

class MainWindow(QMainWindow):
    def __init__(self, dataHandler = dataHandling.dataManager(), CameraApp = CA.App()):
        super().__init__()
        self.dataHandler = dataHandler
        self.CameraApp = CameraApp
        self.CameraApp.setLiveCallback(self.liveCallback)
        self.outputPath = "OUTPUT_IMAGES"

        self.initUI()
        self.CameraApp.run()

    def initUI(self):
        self.setWindowTitle("Experiment Setup")

        # Main layout container
        main_widget = QWidget()
        main_layout = QHBoxLayout()


        ## Experimental Setup Section
        experiment_layout = QVBoxLayout()
        self.experiment_label = QLabel("Experiement Setup Section")
        experiment_layout.addWidget(self.experiment_label)
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
        main_layout.addLayout(experiment_layout)


        ## Imaging Section
        imaging_layout = QVBoxLayout()
        self.imaging_label = QLabel("Imaging Section")
        imaging_layout.addWidget(self.imaging_label)
        # Livefeed
        self.livefeel_label = QLabel(self)
        self.livefeel_label.setScaledContents(True)
        imaging_layout.addWidget(self.livefeel_label)
        # Brightness Value
        self.brightness_label = QLabel("Placeholder") ## Needs to be implemented
        imaging_layout.addWidget(self.brightness_label)
        # Snap and Calibrate Buttons
        imaging_buttons_layout = QHBoxLayout()
        self.snap_push_button = QPushButton("Snap Image")
        self.snap_push_button.clicked.connect(self.snapImage)
        imaging_buttons_layout.addWidget(self.snap_push_button)
        self.cam_calib_push_button = QPushButton("Calibration")
        # self.cam_calib_push_button.clicked.connect(ToDo)
        imaging_buttons_layout.addWidget(self.cam_calib_push_button)
        imaging_layout.addLayout(imaging_buttons_layout)
        main_layout.addLayout(imaging_layout)


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

    def liveCallback(self):
        img = QImage(self.CameraApp.buf, self.CameraApp.width, self.CameraApp.height, (self.CameraApp.width * 24 + 31) // 32 * 4, QImage.Format_RGB888)
        img = img.mirrored(horizontally=False, vertically=True)
        self.livefeel_label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        self.CameraApp.closeCam()

    def snapImage(self):
        print("Snap!")
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.CameraApp.snapImage(os.path.join(self.outputPath, timestamp))

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()