import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *

UI_FILE = "06-input-dialog.ui"
PROGRAM_TITLE = "input-dialog"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)

        self.textEdit.setReadOnly(True)
        self.btnName.clicked.connect(self.inputName)
        self.btnSeason.clicked.connect(self.inputSeason)
        self.btnColor.clicked.connect(self.inputColor)
        self.btnFont.clicked.connect(self.inputFont)
        self.btnFile.clicked.connect(self.openFile)
        self.lineEdit.returnPressed.connect(self.question)
    

    def question(self):
        text = self.lineEdit.text()

        if text.isdigit():
            self.textEdit.append(text)
        else:
            retval = QMessageBox.question(self,
               "QMessageBox - question",
               "Are you sure you want to enter a number?",
               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
               QMessageBox.StandardButton.No)
            if retval == QMessageBox.StandardButton.Yes:
                self.textEdit.append(text)

        self.lineEdit.clear()


    def inputNumber(self):
        text = self.lineEdit.text()
        if text.isdigit():
            self.textEdit.append(text)
        else:
            QMessageBox.warning(self, "QMessageBox - setText", "Please enter only numbers")
        self.lineEdit.clear()
    
    
    def openFile(self):
        name = QFileDialog.getOpenFileName(self, "Open File", "./", "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.ico *.svg)")

        if name[0]:
            with open(name[0], "r") as file:
                data = file.read()
                self.textEdit.append(data)

    def inputFont(self):
        font, ok = QFontDialog.getFont()
        if ok and font:
            info = QFontInfo(font)
            self.textEdit.append(info.family() + info.styleName())
            self.textEdit.selectAll()
            self.textEdit.setFont(font)
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)

    def inputColor(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.textEdit.append("Color")
            self.textEdit.selectAll()
            self.textEdit.setTextColor(color)
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)

    def inputName(self):
        text, ok = QInputDialog.getText(self, "QInputDialog - Name", "User name: " )

        if ok and text:
            self.textEdit.append(text)

    def inputSeason(self):
        items = ["Spring", "Summer", "Fall", "Winter"]
        item, ok = QInputDialog.getItem(self, "QInputDialog - Season", "Season: ", items, 0, False)
        if ok and item:
            self.textEdit.append(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())