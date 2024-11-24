
import os
import sys
import dataHandling
import amcam
from datetime import datetime
import CameraApp as CA
from PySide6.QtCore import QDate, QDir, QStandardPaths, Qt, QUrl, Slot, Signal
from PySide6.QtGui import QAction, QGuiApplication, QDesktopServices, QIcon, QImage, QPixmap, QTransform
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QTabWidget, QToolBar, QVBoxLayout, QWidget,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox, QCheckBox)
from PySide6.QtMultimedia import (QCamera, QImageCapture,
                                  QCameraDevice, QMediaCaptureSession,
                                  QMediaDevices)
from PySide6.QtMultimediaWidgets import QVideoWidget

class MainWindow(QMainWindow):
    def __init__(self):

        self.outputPath = "OUTPUT_IMAGES"

        super().__init__()
        self.setWindowTitle("Experiment Setup")

        self.DApp = CA.App(self.liveCallback)
        self.initUI()
        self.DApp.run()

    def initUI(self):
        # Main layout container
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        ## Display Label
        self.dispLabel = QLabel("Livefeed")
        main_layout.addWidget(self.dispLabel)
        ## Display
        self.livefeel_label = QLabel(self)
        self.livefeel_label.setScaledContents(True)
        # self.livefeel_label.move(0, 30)
        # self.livefeel_label.resize(self.geometry().width(), self.geometry().height())
        main_layout.addWidget(self.livefeel_label)
        ## Snap Button
        self.SnapPB = QPushButton("Snap!")
        self.SnapPB.clicked.connect(self.snapImage)
        main_layout.addWidget(self.SnapPB)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def liveCallback(self):
        img = QImage(self.DApp.buf, self.DApp.width, self.DApp.height, (self.DApp.width * 24 + 31) // 32 * 4, QImage.Format_RGB888)
        img = img.mirrored(horizontally=False, vertically=True)
        self.livefeel_label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        self.DApp.closeCam()

    def snapImage(self):
        print("Snap!")
        time = datetime.now()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.DApp.snapImage(os.path.join(self.outputPath, timestamp))
    

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()