import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import Qt

UI_FILE = "05-color-font.ui"
PROGRAM_TITLE = "color-font"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)
        self.addButton.clicked.connect(self.addText)

        self.ubuntuButton.clicked.connect(lambda: self.setFont("Ubuntu"))
        self.nanumButton.clicked.connect(lambda: self.setFont("NanumGothic"))

        self.redButton.clicked.connect(lambda: self.setTextColor(255, 0, 0))
        self.greenButton.clicked.connect(lambda: self.setTextColor(0, 255, 0))
        self.blueButton.clicked.connect(lambda: self.setTextColor(0, 0, 255))

        self.fontSizeButton.clicked.connect(self.setTextSize)
        self.fontSizeLine.returnPressed.connect(self.setTextSize)
        self.fontSizeLine.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.fontSizeLine.setValidator(QIntValidator(1, 99))

    def addText(self):
        input = self.inputText.toPlainText()
        self.inputText.clear()
        self.outputText.append(input)

    def setFont(self, fontName):
        font = QFont(fontName, 11)
        self.outputText.setFont(font)

    def setTextColor(self, r, g, b):
        color = QColor(r, g, b)
        self.outputText.selectAll()
        self.outputText.setTextColor(color)
        self.outputText.moveCursor(QTextCursor.MoveOperation.End)

    def setTextSize(self):
        if not self.fontSizeLine.text().isdigit():
            return
        size = int(self.fontSizeLine.text())
        self.outputText.selectAll()
        self.outputText.setFontPointSize(size)
        self.outputText.moveCursor(QTextCursor.MoveOperation.End)
        self.fontSizeLine.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())