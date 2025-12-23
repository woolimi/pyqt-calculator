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

        min = self.spinBox.minimum()
        max = self.spinBox.maximum()
        step = self.spinBox.singleStep()

        self.editMin.setText(str(min))
        self.editMax.setText(str(max))
        self.editStep.setText(str(step))

        self.slider.setRange(int(min), int(max))
        self.slider.setSingleStep(int(step))

        self.btnApply.clicked.connect(self.apply)
        self.spinBox.valueChanged.connect(self.changeSpinBox)
        self.slider.valueChanged.connect(self.changeSlider)
        
        self.btnSave.clicked.connect(self.saveImage)
        self.btnOpen.clicked.connect(self.openImage)

        url = "https://imageio.forbes.com/specials-images/imageserve/61b1f75e9bdd78e1c08fdd64/A-funny-labrador-dog-with-a-curiously-placed-bubble-in-its-behind-/0x0.jpg?crop=922%2C956%2Cx0%2Cy279%2Csafe&width=960&dpr=1"
        image = urllib.request.urlopen(url).read()

        self.pixmap = QPixmap()
        # self.pixmap.load("../data/cat.png")
        self.pixmap.loadFromData(image)
        self.pixmap = self.pixmap.scaled(self.labelPixmap.width(), self.labelPixmap.height())
        self.labelPixmap.setPixmap(self.pixmap)
        self.labelPixmap.resize(self.labelPixmap.pixmap().width(), self.labelPixmap.pixmap().height())

    def changeSlider(self):
        actualValue = self.slider.value()
        self.sliderValue.setText(str(actualValue))
        self.spinBox.setValue(actualValue)

    def changeSpinBox(self):
        actualValue = self.spinBox.value()
        self.spinBoxValue.setText(str(actualValue))
        self.slider.setValue(actualValue)

    def apply(self):
        min = self.editMin.text()
        max = self.editMax.text()
        step = self.editStep.text()

        self.spinBox.setRange(int(min), int(max))
        self.spinBox.setSingleStep(int(step))

        self.slider.setRange(int(min), int(max))
        self.slider.setSingleStep(int(step))
    
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
            self.pixmap = QPixmap(file_path)
            if not self.pixmap.isNull():
                # Scale image to fit labelPixmap
                scaled_pixmap = self.pixmap.scaled(
                    self.labelPixmap.width(), 
                    self.labelPixmap.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.labelPixmap.setPixmap(scaled_pixmap)
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