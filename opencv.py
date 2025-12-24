import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
import cv2, imutils
from MyThread import MyTimer
import datetime

UI_FILE = "opencv.ui"
PROGRAM_TITLE = "opencv"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)

        self.pixmap = QPixmap()
        self.cameraOn = False
        self.cameraTimer = MyTimer()
        self.cameraTimer.setInterval(0.05)
        self.count = 0

        self.recording = False
        self.btnRecord.hide()
        self.recordTimer = MyTimer()
        self.recordTimer.setInterval(0.05)

        self.btnCapture.hide()
        
        self.btnOpen.clicked.connect(self.openFile)
        self.btnCamera.clicked.connect(self.clickCamera)
        self.cameraTimer.timeout.connect(self.updateCamera)
        self.btnRecord.clicked.connect(self.clickRecord)
        self.recordTimer.timeout.connect(self.updateRecord)
        self.btnCapture.clicked.connect(self.clickCapture)

    def clickCapture(self):
        self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.now + ".jpg"
        image_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image_bgr)

    def updateRecord(self):
        self.labelTime.setText(str(self.count))
        self.count += 1
        image_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        self.writer.write(image_bgr)

    def startRecording(self):
        self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.now + ".avi"

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.writer = cv2.VideoWriter(filename, self.fourcc, 20.0, (w, h))
        self.recordTimer.start()

    def stopRecording(self):
        self.recordTimer.stop()

        if self.recording == True:
            self.writer.release()
            self.recording = False

    def clickRecord(self):
        if not self.recording:
            self.btnRecord.setText("Rec Stop")
            self.recording = True
            self.startRecording()
        else:
            self.btnRecord.setText("Rec Start")
            self.recording = False
            self.stopRecording()

    def updateCamera(self):
        retVal, image = self.video.read()
        if retVal:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h,w,c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)

    def clickCamera(self):
        if not self.cameraOn:
            self.btnCamera.setText("Camera Off")
            self.cameraOn = True
            self.cameraTimer.start()
            self.video = cv2.VideoCapture(-1)
            self.btnRecord.show()
            self.btnCapture.show()
        else:
            self.btnCamera.setText("Camera On")
            self.cameraOn = False
            self.cameraTimer.stop()
            self.video.release()
            self.btnRecord.hide()
            self.stopRecording()
            self.btnCapture.hide()
    
    def openFile(self):
        file = QFileDialog.getOpenFileName(filter="Image (*.png *.jpg)")
        image = cv2.imread(file[0])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h,w,c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())