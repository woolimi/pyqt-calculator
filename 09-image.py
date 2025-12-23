"""
이미지 리사이징 로직 설명:

1. 파일 오픈 및 읽기:
   - openImage(): QFileDialog로 이미지 파일 선택
   - 선택한 파일을 QPixmap으로 로드
   - loadAndDisplayImage() 호출하여 이미지 표시

2. 초기 이미지 로드 (loadAndDisplayImage):
   - 원본 이미지를 self.originalPixmap에 저장
   - labelPixmap의 폭(width)을 max_size로 설정
   - spinBox/slider의 최대값을 max_size로 설정
   - 초기값을 max_size로 설정
   - 원본 이미지를 종횡비 유지하면서 폭을 max_size로 리사이즈
   - 리사이즈된 이미지를 labelPixmap에 표시

3. 리사이즈 변화 (updateImageSize):
   - spinBox/slider 값(value)이 변경될 때 호출
   - value는 이미지의 폭(width)을 의미
   - 원본 이미지(self.originalPixmap)를 종횡비 유지하면서 폭을 value로 리사이즈
   - 리사이즈된 이미지를 labelPixmap에 직접 표시
   - changeSlider()와 changeSpinBox()에서 호출

4. 저장 (saveImage):
   - 현재 labelPixmap에 표시된 pixmap을 가져옴
   - QFileDialog로 저장 경로 선택
   - 선택한 경로에 PNG 형식으로 저장
   - 저장되는 이미지는 현재 표시된 크기(종횡비 유지된 리사이즈 이미지)

주의사항:
- 모든 리사이징은 종횡비를 유지하면서 폭을 기준으로 리사이즈
- 원본 이미지는 self.originalPixmap에 보관되어 항상 원본에서 리사이즈
- max 값은 labelPixmap의 폭을 초과할 수 없음
- spinBox/slider 값은 이미지의 폭(width)을 의미
"""

import sys
import re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import Qt
import urllib.request

UI_FILE = "09-image.ui"
PROGRAM_TITLE = "image"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)

        self.spinBox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editMin.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editMax.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editStep.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spinBoxValue.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.editMin.setValidator(QIntValidator())
        self.editMax.setValidator(QIntValidator())
        self.editStep.setValidator(QIntValidator())

        # Initialize originalPixmap
        self.originalPixmap = QPixmap()

        # Calculate max value based on labelPixmap width
        max_size = self.labelPixmap.width()
        self.spinBox.setMaximum(max_size)
        self.slider.setMaximum(max_size)
        self.spinBox.setValue(max_size)
        self.slider.setValue(max_size)
        self.editMax.setText(str(max_size))

        min = self.spinBox.minimum()
        step = self.spinBox.singleStep()

        self.editMin.setText(str(min))
        self.editStep.setText(str(step))

        self.slider.setRange(int(min), int(max_size))
        self.slider.setSingleStep(int(step))

        self.btnApply.clicked.connect(self.apply)
        self.spinBox.valueChanged.connect(self.changeSpinBox)
        self.slider.valueChanged.connect(self.changeSlider)
        
        self.btnSave.clicked.connect(self.saveImage)
        self.btnOpen.clicked.connect(self.openImage)

        # Load initial image
        url = "https://imageio.forbes.com/specials-images/imageserve/61b1f75e9bdd78e1c08fdd64/A-funny-labrador-dog-with-a-curiously-placed-bubble-in-its-behind-/0x0.jpg?crop=922%2C956%2Cx0%2Cy279%2Csafe&width=960&dpr=1"
        image = urllib.request.urlopen(url).read()

        initial_pixmap = QPixmap()
        initial_pixmap.loadFromData(image)
        self.loadAndDisplayImage(initial_pixmap)

    def loadAndDisplayImage(self, pixmap):
        """Load image and display it, setting up max values and initial display"""
        if pixmap.isNull():
            return
        
        # Store original pixmap
        self.originalPixmap = pixmap
        
        # Recalculate max value based on labelPixmap width
        max_size = self.labelPixmap.width()
        self.spinBox.setMaximum(max_size)
        self.slider.setMaximum(max_size)
        self.editMax.setText(str(max_size))
        
        # Set initial value to max
        self.spinBox.setValue(max_size)
        self.slider.setValue(max_size)
        
        # Resize original image maintaining aspect ratio, width = max_size
        resized_pixmap = pixmap.scaledToWidth(
            max_size,
            Qt.TransformationMode.SmoothTransformation
        )
        self.labelPixmap.setPixmap(resized_pixmap)

    def changeSlider(self):
        actualValue = self.slider.value()
        self.sliderValue.setText(str(actualValue))
        self.spinBox.setValue(actualValue)
        self.updateImageSize(actualValue)

    def updateImageSize(self, value):
        """Update image size based on spinBox/slider value (value = width)"""
        if self.originalPixmap.isNull():
            return
        
        # Resize original image maintaining aspect ratio, width = value
        resized_pixmap = self.originalPixmap.scaledToWidth(
            value,
            Qt.TransformationMode.SmoothTransformation
        )

        self.labelPixmap.setPixmap(resized_pixmap)

    def changeSpinBox(self):
        actualValue = self.spinBox.value()
        self.spinBoxValue.setText(str(actualValue))
        self.slider.setValue(actualValue)
        self.updateImageSize(actualValue)

    def apply(self):
        min_text = self.editMin.text()
        max_text = self.editMax.text()
        step = self.editStep.text()

        # Ensure max doesn't exceed labelPixmap width
        max_size = self.labelPixmap.width()
        max_value = min(int(max_text), max_size)
        min_value = int(min_text)
        
        # Update max value in editMax if it was limited
        if int(max_text) > max_size:
            self.editMax.setText(str(max_size))
            max_value = max_size
        if int(min_text) > max_value:
            self.editMin.setText(str(max_value))
            min_value = max_value

        self.spinBox.setRange(min_value, max_value)
        self.spinBox.setSingleStep(int(step))

        self.slider.setRange(min_value, max_value)
        self.slider.setSingleStep(int(step))
        
        # Ensure current value doesn't exceed new max
        current_value = min(self.spinBox.value(), max_value)
        self.spinBox.setValue(current_value)
        self.slider.setValue(current_value)
        
        # Update image size with current value
        self.updateImageSize(current_value)
    
    def openImage(self):
        # Open file dialog to select image file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "./",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.ico *.svg);;All Files (*)"
        )
        
        if file_path:
            # Load image from file
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.loadAndDisplayImage(pixmap)
            else:
                QMessageBox.warning(self, "Error", "Failed to load image file")
    
    def saveImage(self):
        # Open file dialog to get save file name
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Image", 
            "./", 
            "PNG Images (*.png);;All Files (*)"
        )
        
        if file_path:
            # Ensure file has .png extension
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Get current pixmap from label
            current_pixmap = self.labelPixmap.pixmap()
            if current_pixmap and not current_pixmap.isNull():
                # Save the pixmap to file as PNG
                if current_pixmap.save(file_path, "PNG"):
                    QMessageBox.information(self, "Success", f"Image saved to {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save image")
            else:
                QMessageBox.warning(self, "Error", "No image to save")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())