import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QRegularExpressionValidator, QValidator
from PyQt6 import uic
from PyQt6.QtCore import QRegularExpression, Qt

UI_FILE = "08-table.ui"
PROGRAM_TITLE = "table"

from_class = uic.loadUiType(UI_FILE)[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(PROGRAM_TITLE)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Gender", "BirthDate"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.btnAdd.clicked.connect(self.add)

        gender_validator = QRegularExpressionValidator(QRegularExpression(r"[F|M]"), self.editGender)
        self.ip_validator = QRegularExpressionValidator(QRegularExpression(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"), self.editIp)
        self.editGender.setValidator(gender_validator)
        self.editIp.setValidator(self.ip_validator)
        self.editName.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editGender.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editBirthDate.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editIp.setAlignment(Qt.AlignmentFlag.AlignRight)

    def checkInputs(self):
        if self.editName.text() == "":
            QMessageBox.warning(self, "Warning", "Name is required")
            return False
        if self.editGender.text() == "":
            QMessageBox.warning(self, "Warning", "Gender is required")
            return False
        if self.editBirthDate.text() == "":
            QMessageBox.warning(self, "Warning", "BirthDate is required")
            return False
        if self.editIp.text() == "":
            QMessageBox.warning(self, "Warning", "IP is required")
            return False
        
        # Check if IP address matches the validator pattern
        ip_text = self.editIp.text()
        state, _, _ = self.ip_validator.validate(ip_text, 0)
        if state != QValidator.State.Acceptable:
            QMessageBox.warning(self, "Warning", "Invalid IP address format")
            return False
            
        return True

    def add(self):
        if not self.checkInputs():
            return
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        self.table.setItem(row_index, 0, QTableWidgetItem(self.editName.text()))
        self.table.setItem(row_index, 1, QTableWidgetItem(self.editGender.text()))
        self.table.setItem(row_index, 2, QTableWidgetItem(self.editBirthDate.text()))
        
        # Set center alignment for all cells in the row
        self.table.item(row_index, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.item(row_index, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.item(row_index, 2).setTextAlignment(Qt.AlignmentFlag.AlignCenter)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())