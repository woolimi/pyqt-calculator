import sys
import re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
from decimal import Decimal, getcontext

from_class = uic.loadUiType("calc.ui")[0]
getcontext().prec = 10

# operands 에는 string 숫자가 들어간다.
# operands 가 1개일 경우 operator 를 누르면
# - operator 를 누르면 operators 리스트에 추가, 단 1개만 추가되며 새로운 operator 가 있는경우 기존 operator 를 교체한다.
# operands 가 2개일 경우 operator 를 누르면
# - operator 2개와 operands 앞의 것과 연산을 해서 operands 리스트를 1개로 만든다
# - 연산된 operator 삭제, 새로운 operator 추가

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Calculator")
        self.operands = [] # string list
        self.operators = [] # string list +, -, *, /
        self.has_error = False  # 에러 상태 플래그

        self.lineEdit.setText("0")

        for i in range(10):
            button = getattr(self, f'number{i}', None)
            if button:
                button.clicked.connect(self.clickNumber(i))
        self.dot.clicked.connect(self.clickDot)
        self.cleanEntryBtn.clicked.connect(self.cleanEntry)
        self.cleanAllBtn.clicked.connect(self.cleanAll)
        self.plus.clicked.connect(self.calcPlus)
        self.minus.clicked.connect(self.calcMinus)
        self.multi.clicked.connect(self.calcMulti)
        self.div.clicked.connect(self.calcDiv)
        self.sign.clicked.connect(self.calcSign)
        self.equalBtn.clicked.connect(self.calcEqual)

    def _getAcc(self):
        # 제일 마지막 요소를 꺼냄. 요소가 없다면 요소를 만듦 ["0"]
        if not self.operands:
            self.operands = ["0"]
        acc = self.operands[-1]

        return acc

    def _setAcc(self, acc):
        # operands 설정
        if not self.operators:
            # operator가 없으면 첫 번째 operand 업데이트
            if not self.operands:
                self.operands = [acc]
            else:
                self.operands[0] = acc
        elif len(self.operators) == 1:
            # operator가 1개면 두 번째 operand 설정
            if len(self.operands) < 2:
                self.operands.append(acc)
            else:
                self.operands[1] = acc


    def clickNumber(self, num):
        def func():
            # 에러 상태면 연산 불가
            if self.has_error:
                return
            
            # 연산자가 있으면 두 번째 operand, 없으면 첫 번째 operand 사용
            if self.operators:
                # 두 번째 operand가 없으면 새로 만들기
                if len(self.operands) < 2:
                    self.operands.append("0")
                operand_idx = 1
            else:
                # 첫 번째 operand가 없으면 만들기
                if not self.operands:
                    self.operands = ["0"]
                operand_idx = 0
            
            # 공통 로직: accumulator 가져오기, "0" 처리, 숫자 추가
            acc = self.operands[operand_idx]
            if acc == "0":
                acc = ""
            acc += str(num)
            self.operands[operand_idx] = acc
            
            self.render(acc)
        return func
    
    def clickDot(self):
        # 에러 상태면 연산 불가
        if self.has_error:
            return
        
        # 연산자가 있으면 두 번째 operand, 없으면 첫 번째 operand 사용
        if self.operators:
            if len(self.operands) < 2:
                self.operands.append("0")
            operand_idx = 1
        else:
            if not self.operands:
                self.operands = ["0"]
            operand_idx = 0
        
        # 공통 로직: accumulator 가져오기, 패턴 체크, 점 추가
        acc = self.operands[operand_idx]
        if re.match(r'^-?\d+$', acc):
            acc += "."
            self.operands[operand_idx] = acc
            self.render(acc)

    def cleanEntry(self):
        acc = self._getAcc()
        acc = "0"
        self._setAcc(acc)
        self.render(acc)

    def cleanAll(self):
        self.operands = ["0"]
        self.operators = []
        self.has_error = False  # 에러 상태 초기화
        self.render(self._getAcc())

    def render(self, str):
        self.lineEdit.setText(str)

    def _setOperator(self, operator):
        """연산자 설정 및 계산 수행"""
        # 에러 상태면 연산 불가
        if self.has_error:
            return
        
        # 피연산자가 없으면 초기화
        if not self.operands:
            self.operands = ["0"]
        
        # 피연산자 1개일때
        if len(self.operands) == 1:
            self.operators = [operator]
        elif len(self.operands) == 2:
            # 기존 연산자가 있으면 계산 수행
            if self.operators:
                prev_op = self.operators[0]
                acc = self.calc(prev_op, self.operands[0], self.operands[1])
                # 에러 체크
                if acc == "ERR":
                    self.has_error = True
                    self.operands = ["ERR"]
                    self.operators = []
                    self.render("ERR")
                    return
                # 결과를 operands에 저장 (1개로 만들기)
                self.operands = [acc]
                self.render(acc)
            # 새로운 연산자 설정
            self.operators = [operator]

    def calcPlus(self):
        self._setOperator("+")

    def calcMinus(self):
        self._setOperator("-")

    def calcDiv(self):
        self._setOperator("/")

    def calcMulti(self):
        self._setOperator("*")

    def calcSign(self):
        """부호 변경"""
        # 에러 상태면 연산 불가
        if self.has_error:
            return
        
        # 연산자가 있으면 두 번째 operand, 없으면 첫 번째 operand 사용
        if self.operators:
            if len(self.operands) < 2:
                self.operands.append("0")
            operand_idx = 1
        else:
            if not self.operands:
                self.operands = ["0"]
            operand_idx = 0
        
        # 부호 변경
        acc = self.operands[operand_idx]
        if acc.startswith("-"):
            acc = acc[1:]
        else:
            acc = "-" + acc
        self.operands[operand_idx] = acc
        self.render(acc)

    def calcEqual(self):
        """등호 버튼 - 계산 수행"""
        # 에러 상태면 연산 불가
        if self.has_error:
            return
        
        # 피연산자 2개, 연산자 1개일 때만 계산 수행
        if len(self.operands) == 2 and len(self.operators) == 1:
            operator = self.operators[0]
            acc = self.calc(operator, self.operands[0], self.operands[1])
            
            # 에러 체크
            if acc == "ERR":
                self.has_error = True
                self.operands = ["ERR"]
                self.operators = []
                self.render("ERR")
                return
            
            # 결과를 operands에 저장 (1개로 만들기), operators는 빈 배열로 초기화
            self.operands = []
            self.operators = []
            self.render(acc)

    def calc(self, operator, operand1, operand2):
        """연산 수행"""
        try:
            op1 = Decimal(str(operand1))
            op2 = Decimal(str(operand2))
            if operator == '+':
                result = op1 + op2
            elif operator == '-':
                result = op1 - op2
            elif operator == '*':
                result = op1 * op2
            elif operator == '/':
                if op2 == 0:
                    return "ERR"  # 0으로 나누기 에러
                result = op1 / op2
            else:
                return "ERR"
            # 결과를 문자열로 변환 (불필요한 0 제거)
            result_str = str(result).rstrip('0').rstrip('.')
            return result_str if result_str else "0"
        except Exception as e:
            return "ERR"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())
