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
        self.btnPlay.hide()
        self.btnPause.hide()
        
        self.videoPlaying = False
        self.videoFile = None
        self.writer = None
        
        self.btnOpen.clicked.connect(self.openFile)
        self.btnCamera.clicked.connect(self.clickCamera)
        self.cameraTimer.timeout.connect(self.updateCamera)
        self.btnRecord.clicked.connect(self.clickRecord)
        self.recordTimer.timeout.connect(self.updateRecord)
        self.btnCapture.clicked.connect(self.clickCapture)
        self.btnPlay.clicked.connect(self.clickPlay)
        self.btnPause.clicked.connect(self.clickPause)

    def clickPlay(self):
        if self.videoFile and not self.videoPlaying:
            # 현재 프레임 위치 확인
            current_frame = self.videoFile.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.videoFile.get(cv2.CAP_PROP_FRAME_COUNT)
            
            # 비디오가 끝났다면 처음으로 리셋
            if current_frame >= total_frames - 1:
                self.videoFile.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            self.videoPlaying = True
            self.cameraTimer.start()
            self.btnPause.setEnabled(True)
            self.btnPlay.setEnabled(False)

    def clickPause(self):
        if self.videoFile and self.videoPlaying:
            self.videoPlaying = False
            self.cameraTimer.stop()
            self.btnPause.setEnabled(False)
            self.btnPlay.setEnabled(True)

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
        filename = self.now + ".mp4"

        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.writer = cv2.VideoWriter(filename, self.fourcc, 20.0, (w, h))
        self.recordTimer.start()

    def stopRecording(self):
        self.recordTimer.stop()

        if self.recording == True:
            self.writer.release()
            self.writer = None
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
        # 비디오 파일 재생 중인 경우
        if self.videoFile:
            retVal, image = self.videoFile.read()
            if retVal and self.videoPlaying:
                self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                h, w, c = self.image.shape
                qimage = QImage(self.image.data, w, h, w*c, QImage.Format.Format_RGB888)
                self.pixmap = self.pixmap.fromImage(qimage)
                self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
                self.label.setPixmap(self.pixmap)
            else:
                self.videoPlaying = False
                self.cameraTimer.stop()
                # 프레임 위치는 유지 (clickPlay에서 필요시 리셋)
                self.btnPause.setEnabled(False)
                self.btnPlay.setEnabled(True)
            return
                    
        
        # 카메라 사용 중인 경우
        if self.cameraOn and hasattr(self, 'video'):
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
        file = QFileDialog.getOpenFileName(
            self, 
            "파일 열기", 
            "", 
            "이미지 및 비디오 (*.png *.jpg *.jpeg *.bmp *.avi *.mp4 *.mov *.mkv);;이미지 (*.png *.jpg *.jpeg *.bmp);;비디오 (*.avi *.mp4 *.mov *.mkv)"
        )
        if not file[0]:  # 파일 선택 취소
            return
        filepath = file[0]
        file_ext = filepath.lower().split('.')[-1]

        if file_ext in ['png', 'jpg', 'jpeg', 'bmp']:
            image = cv2.imread(file[0])
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h,w,c = image.shape
            qimage = QImage(image.data, w, h, w*c, QImage.Format.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            self.label.setPixmap(self.pixmap)
            self.btnPlay.hide()
            self.btnPause.hide()
        elif file_ext in ['avi', 'mp4', 'mov', 'mkv']:
            # 카메라가 켜져있으면 먼저 끄기
            if self.cameraOn:
                self.clickCamera()
            
            # 기존 비디오 파일이 있으면 해제
            if self.videoFile:
                self.videoFile.release()
            
            self.videoFile = cv2.VideoCapture(filepath)
            if not self.videoFile.isOpened():
                QMessageBox.warning(self, "오류", "비디오를 불러올 수 없습니다.")
                self.videoFile = None
                return
            
            self.videoPlaying = False
            self.btnPause.show()
            self.btnPlay.show()
            self.btnPause.setEnabled(False)
            self.btnPlay.setEnabled(True)
            # 첫 프레임 표시
            retVal, image = self.videoFile.read()
            if retVal:
                self.videoFile.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 처음으로 되돌리기
                self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                h, w, c = self.image.shape
                qimage = QImage(self.image.data, w, h, w*c, QImage.Format.Format_RGB888)
                self.pixmap = self.pixmap.fromImage(qimage)
                self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
                self.label.setPixmap(self.pixmap)
        else:
            QMessageBox.warning(self, "파일 형식 오류", "지원되지 않는 파일 형식입니다.")
            return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())