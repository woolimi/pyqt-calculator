import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *

from_class = uic.loadUiType("calc.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Calculator")
        self.expr = ""
        self.lineEdit.setText("0")
        # self.lineEdit.textChanged.connect(self.exprChanged)

        self.number0.clicked.connect(self.clickNumber(0))
        self.number1.clicked.connect(self.clickNumber(1))
        self.number2.clicked.connect(self.clickNumber(2))
        self.number3.clicked.connect(self.clickNumber(3))
        self.number4.clicked.connect(self.clickNumber(4))
        self.number5.clicked.connect(self.clickNumber(5))
        self.number6.clicked.connect(self.clickNumber(6))
        self.number7.clicked.connect(self.clickNumber(7))
        self.number8.clicked.connect(self.clickNumber(8))
        self.number9.clicked.connect(self.clickNumber(9))
        self.cleanBtn.clicked.connect(self.clean)
        self.cleanAllBtn.clicked.connect(self.cleanAll)

    def clickNumber(self, num):
        def func():
            self.expr += str(num);
            self.renderExpr()
        return func

    # def exprChanged(self):
    #     self.expr = self.lineEdit.text()

    def clean(self):
        self.expr = self.expr[0:-1]
        if self.expr == "":
            self.expr = 0
        self.renderExpr()

    def cleanAll(self):
        self.expr = "0"
        self.renderExpr()

    def renderExpr(self):
        self.lineEdit.setText(self.expr)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())
