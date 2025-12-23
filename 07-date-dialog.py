import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
from datetime import datetime

UI_FILE = "07-date-dialog.ui"
PROGRAM_TITLE = "date-dialog"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)

        for year in range(1900, datetime.now().year + 1):
            self.cbYear.addItem(str(year))
        for month in range(1, 12 + 1):
            self.cbMonth.addItem(str(month))
        for day in range(1, 31 + 1):
            self.cbDay.addItem(str(day))

        self.cbYear.setCurrentText(str(2000))
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.cbYear.currentIndexChanged.connect(self.printBirthDate)
        self.cbMonth.currentIndexChanged.connect(self.printBirthDate)
        self.cbDay.currentIndexChanged.connect(self.printBirthDate)

        # Set date range: 1900-01-01 to current date
        self.calendarWidget.setMinimumDate(QDate(1900, 1, 1))
        self.calendarWidget.setMaximumDate(QDate.currentDate())

        self.calendarWidget.clicked.connect(self.selectDate)
    
    def selectDate(self):
        date = self.calendarWidget.selectedDate()
        year = date.toString("yyyy")
        month = date.toString("M")
        day = date.toString("d")
        self.cbYear.setCurrentText(year)
        self.cbMonth.setCurrentText(month)
        self.cbDay.setCurrentText(day)
        self.lineEdit.setText(f"{year}-{month.zfill(2)}-{day.zfill(2)}")

    def printBirthDate(self):
        year = self.cbYear.currentText()
        month = self.cbMonth.currentText()
        day = self.cbDay.currentText()
        self.lineEdit.setText(f"{year}-{month.zfill(2)}-{day.zfill(2)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())