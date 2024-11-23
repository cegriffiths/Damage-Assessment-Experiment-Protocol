## DATA HANDLING SCRIPT
## Author: Chris Griffiths
# Date: November 22, 2024
# UBC ENPH 479

## This script will host all of the UIs, including interfacing with the dataHandler, Camera, and general states from runProtocol.

import os
import sys
import dataHandling
from PySide6.QtCore import QDate, QDir, QStandardPaths, Qt, QUrl, Slot
from PySide6.QtGui import QAction, QGuiApplication, QDesktopServices, QIcon
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QTabWidget, QToolBar, QVBoxLayout, QWidget,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox)
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices)
from PySide6.QtMultimediaWidgets import QVideoWidget

# class UIHost:
class MainWindow(QMainWindow):
    def __init__(self, dataHandler = dataHandling.dataManager()):
        super().__init__()
        self.dataHandler = dataHandler
        self.setWindowTitle("Experiment Setup")

        # Main layout container
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Experiment File Selection Dropdown
        file_layout = QHBoxLayout()
        file_label = QLabel("Select File:")
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("No file selected")
        self.file_input.setReadOnly(True)  # Make the file path non-editable
        file_button = QPushButton("Browse")
        file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(file_button)
        main_layout.addLayout(file_layout)

        # EE selection Menu
        EE_dropdown_layout = QHBoxLayout()
        EE_dropdown_label = QLabel("Options:")
        self.EE_dropdown = QComboBox()
        self.EE_dropdown.addItems(["Circular Planar", "Rectangular Planar"])
        EE_dropdown_layout.addWidget(EE_dropdown_label)
        EE_dropdown_layout.addWidget(self.EE_dropdown)
        main_layout.addLayout(EE_dropdown_layout)

        # Number of PnP cycles per sensor input
        PnP_cycles_layout = QHBoxLayout()
        PnP_cycles_label = QLabel("Number of Pick and Place Cycles:")
        self.PnP_cycles_input = QSpinBox()
        self.PnP_cycles_input.setRange(0, 100)  # Set the range for the number input
        self.PnP_cycles_input.setValue(50)  # Default value
        PnP_cycles_layout.addWidget(PnP_cycles_label)
        PnP_cycles_layout.addWidget(self.PnP_cycles_input)
        main_layout.addLayout(PnP_cycles_layout)

        # Imaging Interval input
        Imaging_Interval_layout = QHBoxLayout()
        Imaging_Interval_label = QLabel("Imaging Interval (cycles/image):")
        self.Imaging_Interval_input = QSpinBox()
        self.Imaging_Interval_input.setRange(0, 100)
        self.Imaging_Interval_input.setValue(5)
        Imaging_Interval_layout.addWidget(Imaging_Interval_label)
        Imaging_Interval_layout.addWidget(self.Imaging_Interval_input)
        main_layout.addLayout(Imaging_Interval_layout)

        # Submit Button
        self.Submit_button = QPushButton("Submit")
        self.Submit_button.clicked.connect(self.submit_data)
        main_layout.addWidget(self.Submit_button)

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
        print(f"Experiement File: ", self.experiment_file_path, "\nEnd Effector: ", self.EE, "\nPnP Cycles: ",self.num_PnP_cycles, "\nImaging Interval: ", self.imaging_interval)
        self.dataHandler.experimentFilePath = self.experiment_file_path
        self.dataHandler.EE = self.EE
        self.dataHandler.numPnPCycles = self.num_PnP_cycles
        self.dataHandler.imagingInterval = self.imaging_interval

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()