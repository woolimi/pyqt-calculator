import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *

from_class = uic.loadUiType("Test2.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Test2")
        self.count = 0
        self.label.setText(str(self.count))

        self.countButton.clicked.connect(self.increment)
        self.resetButton.clicked.connect(self.reset)

        self.submitButton.clicked.connect(self.submit)
        # self.inputLine.textChanged.connect(self.change)
        self.inputLine.returnPressed.connect(self.returnPressed)

    def increment(self):
        self.count += 1
        self.label.setText(str(self.count))

    def reset(self):
        self.count = 0
        self.label.setText(str(self.count))

    def submit(self):
        self.label.setText(self.lineEdit.text())
        self.lineEdit.clear()
    
    def change(self):
        self.outputLine.setText(self.inputLine.text())

    def returnPressed(self):
        self.outputLine.setText(self.inputLine.text())
        self.inputLine.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())