import sys
import re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
from decimal import Decimal, getcontext

from_class = uic.loadUiType("calc.ui")[0]
getcontext().prec = 10

# ========== 헬퍼 함수 ==========
def format_result(result):
    """계산 결과를 문자열로 포맷팅 (불필요한 0 제거)"""
    result_str = str(result).rstrip('0').rstrip('.')
    return result_str if result_str else "0"


def calculate(operator, operand1, operand2):
    """
    실제 계산 수행 (순수 함수)
    
    Args:
        operator: 연산자 (+, -, *, /)
        operand1: 첫 번째 피연산자
        operand2: 두 번째 피연산자
    
    Returns:
        계산 결과 문자열 또는 "ERR"
    """
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
        
        return format_result(result)
    except Exception:
        return "ERR"


# ========== 클래스 ==========

"""
쌀집 계산기 상태 관리 규칙:

1. operands: 문자열 숫자 리스트 (예: ["123", "456"])
   - 피연산자들을 문자열로 저장
   - 최대 2개까지 저장 가능

2. operators: 연산자 리스트 (예: ["+"], ["-"])
   - 연산자를 문자열로 저장
   - 항상 0개 또는 1개만 유지

3. 숫자 버튼 클릭 시 동작:
   - 연산자가 있으면: 두 번째 operand에 숫자 추가 (없으면 "0" 생성 후 추가)
   - 연산자가 없으면: 첫 번째 operand에 숫자 추가 (없으면 "0" 생성 후 추가)
   - 현재 값이 "0"이면 빈 문자열로 초기화 후 숫자 추가
   - 현재 값이 "-0"이면 "-"로 초기화 후 숫자 추가
   - 등호 버튼 후 상태(operands가 빈 배열)에서는 새로운 피연산자로 시작

4. 연산자 버튼 클릭 시 동작:
   - operands가 1개일 때: operators에 연산자 추가 (기존 연산자가 있으면 교체)
   - operands가 2개일 때: 
     * 기존 연산자로 계산 수행 (operands[0] 연산자 operands[1])
     * 결과를 operands[0]에 저장, operands는 1개로 축소
     * 새로운 연산자를 operators에 설정

5. 등호 버튼 클릭 시 동작:
   - operands가 2개, operators가 1개일 때만 계산 수행
   - 계산 후 operands와 operators 모두 초기화
   - 결과값은 화면에만 표시 (다음 숫자 입력 시 새로 시작)
"""

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

    # ========== 헬퍼 메서드 ==========
    
    def _checkError(self):
        """에러 상태 확인"""
        return self.has_error
    
    def _handleError(self, error_msg="ERR"):
        """에러 처리"""
        self.has_error = True
        self.operands = [error_msg]
        self.operators = []
        self.render(error_msg)
    
    def _getOperandIndex(self):
        """
        현재 입력할 operand의 인덱스를 반환
        연산자가 있으면 두 번째 operand(1), 없으면 첫 번째 operand(0)
        """
        if self.operators:
            # 두 번째 operand가 없으면 생성
            if len(self.operands) < 2:
                self.operands.append("0")
            return 1
        else:
            # 첫 번째 operand가 없으면 생성
            if not self.operands:
                self.operands = ["0"]
            return 0
    
    def _getAcc(self):
        """마지막 operand 값을 반환 (없으면 "0" 생성)"""
        if not self.operands:
            self.operands = ["0"]
        return self.operands[-1]

    def _setAcc(self, acc):
        """operand 값 설정"""
        if not self.operators:
            # 연산자가 없으면 첫 번째 operand 업데이트
            if not self.operands:
                self.operands = [acc]
            else:
                self.operands[0] = acc
        elif len(self.operators) == 1:
            # 연산자가 1개면 두 번째 operand 설정
            if len(self.operands) < 2:
                self.operands.append(acc)
            else:
                self.operands[1] = acc
    
    def _performCalculation(self, operator, operand1, operand2):
        """계산 수행 및 에러 처리"""
        result = calculate(operator, operand1, operand2)
        if result == "ERR":
            self._handleError()
            return None
        return result


    # ========== 입력 메서드 ==========
    
    def clickNumber(self, num):
        """숫자 버튼 클릭 처리"""
        def func():
            if self._checkError():
                return
            
            operand_idx = self._getOperandIndex()
            acc = self.operands[operand_idx]
            
            # "0"이면 빈 문자열로 초기화, "-0"이면 "-"로 초기화 후 숫자 추가
            if acc == "0":
                acc = ""
            elif acc == "-0":
                acc = "-"
            acc += str(num)
            
            self.operands[operand_idx] = acc
            self.render(acc)
        return func
    
    def clickDot(self):
        """소수점 버튼 클릭 처리"""
        if self._checkError():
            return
        
        operand_idx = self._getOperandIndex()
        acc = self.operands[operand_idx]
        
        # 정수 패턴이면 소수점 추가
        if re.match(r'^-?\d+$', acc):
            acc += "."
            self.operands[operand_idx] = acc
            self.render(acc)

    def cleanEntry(self):
        """현재 입력값만 초기화 (CE 버튼)"""
        acc = self._getAcc()
        acc = "0"
        self._setAcc(acc)
        self.render(acc)

    def cleanAll(self):
        """모든 상태 초기화 (AC 버튼)"""
        self.operands = ["0"]
        self.operators = []
        self.has_error = False
        self.render(self._getAcc())

    def render(self, value):
        """화면에 값 표시"""
        self.lineEdit.setText(value)

    # ========== 연산 메서드 ==========
    
    def _setOperator(self, operator):
        """연산자 설정 및 필요시 계산 수행"""
        if self._checkError():
            return
        
        # 피연산자가 없으면 초기화
        if not self.operands:
            self.operands = ["0"]
        
        if len(self.operands) == 1:
            # 피연산자 1개: 연산자만 설정
            self.operators = [operator]
        elif len(self.operands) == 2:
            # 피연산자 2개: 기존 연산으로 계산 후 새 연산자 설정
            if self.operators:
                prev_op = self.operators[0]
                result = self._performCalculation(prev_op, self.operands[0], self.operands[1])
                if result is None:  # 에러 발생
                    return
                self.operands = [result]
                self.render(result)
            self.operators = [operator]

    def calcPlus(self):
        """덧셈 연산자 설정"""
        self._setOperator("+")

    def calcMinus(self):
        """뺄셈 연산자 설정"""
        self._setOperator("-")

    def calcDiv(self):
        """나눗셈 연산자 설정"""
        self._setOperator("/")

    def calcMulti(self):
        """곱셈 연산자 설정"""
        self._setOperator("*")

    def calcSign(self):
        """부호 변경 (+/- 버튼)"""
        if self._checkError():
            return
        
        operand_idx = self._getOperandIndex()
        acc = self.operands[operand_idx]
        
        # 부호 토글
        if acc.startswith("-"):
            acc = acc[1:]
        else:
            acc = "-" + acc
        
        self.operands[operand_idx] = acc
        self.render(acc)

    def calcEqual(self):
        """등호 버튼 - 계산 수행 및 상태 초기화"""
        if self._checkError():
            return
        
        # 피연산자 2개, 연산자 1개일 때만 계산 수행
        if len(self.operands) == 2 and len(self.operators) == 1:
            operator = self.operators[0]
            result = self._performCalculation(operator, self.operands[0], self.operands[1])
            
            if result is None:  # 에러 발생
                return
            
            # 계산 완료 후 상태 초기화 (연산자 제거, 피연산자는 결과값만 유지)
            self.operands = []
            self.operators = []
            self.render(result)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())
