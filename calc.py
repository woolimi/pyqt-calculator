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
    result_str = str(result)
    # 소수점이 있는 경우에만 끝의 0과 소수점 제거
    if '.' in result_str:
        result_str = result_str.rstrip('0').rstrip('.')
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

1. 상태 변수:
   - accumulator: 문자열 숫자 (예: "123")
     * 이전 계산 결과 또는 첫 번째 피연산자를 저장
     * 계산이 완료되거나 초기화될 때까지 유지
   
   - lineEdit: 화면에 표시되는 현재 숫자 (예: "456")
     * 사용자가 입력 중인 숫자를 표시
     * 항상 유효한 숫자 문자열을 유지 ("0" 기본값)
   
   - operator: 연산자 문자열 또는 None (예: "+", "-", "*", "/", None)
     * 현재 설정된 연산자를 저장
     * None이면 연산자가 설정되지 않은 상태
   
   - operator_entered: 불린 플래그
     * 연산자가 입력되었는지 여부를 나타냄
     * True이면 다음 숫자 입력 시 새로운 숫자로 시작해야 함

2. 숫자 버튼 클릭 시 동작:
   - lineEdit에서 현재 숫자를 읽어옴
   - operator_entered 플래그가 True이면:
     * 새로운 숫자 입력 시작 (lineEdit을 "0" 또는 빈 문자열로 초기화)
     * operator_entered 플래그를 False로 설정
   - operator_entered 플래그가 False이면:
     * 기존 숫자에 숫자를 추가
   - 현재 값이 "0"이면 빈 문자열로 초기화 후 숫자 추가
   - 현재 값이 "-0"이면 "-"로 초기화 후 숫자 추가
   - 숫자 입력 후 operator_entered 플래그를 False로 설정
   - 최종 숫자를 lineEdit에 표시

3. 연산자 버튼 클릭 시 동작:
   - lineEdit의 숫자는 건드리지 않음 (화면 표시 유지)
   - accumulator와 operator가 모두 설정되어 있고, lineEdit에 유효한 숫자가 있으면:
     * 이전 계산 수행 (accumulator 연산자 lineEdit의 숫자)
     * 결과를 accumulator에 저장하고 lineEdit에 표시
   - accumulator가 없거나 비어있으면:
     * lineEdit의 현재 값을 accumulator에 저장
   - operator에 새로운 연산자를 저장
   - operator_entered 플래그를 True로 설정

4. 등호 버튼 클릭 시 동작:
   - accumulator와 operator가 모두 설정되어 있고, lineEdit에 유효한 숫자가 있을 때만 계산 수행
   - 계산 수행 (accumulator 연산자 lineEdit의 숫자)
   - 결과를 accumulator에 저장하고 lineEdit에 표시
   - operator를 None으로 초기화
   - operator_entered 플래그를 False로 설정
"""

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Calculator")
        self.accumulator = None  # 문자열 숫자 또는 None
        self.operator = None  # 연산자 문자열 ("+", "-", "*", "/") 또는 None
        self.operator_entered = False  # 연산자 입력 플래그
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
        self.accumulator = error_msg
        self.operator = None
        self.operator_entered = False
        self.render(error_msg)
    
    def _performCalculation(self, operator, operand1, operand2):
        """계산 수행 및 에러 처리"""
        result = calculate(operator, operand1, operand2)
        if result == "ERR":
            self._handleError()
            return None
        return result
    
    def _isAfterEqual(self):
        """등호 실행 후 상태인지 확인
        
        Returns:
            bool: 등호 실행 후 상태인지 여부 (True면 등호 실행 후, False면 그 외)
        """
        return self.accumulator is not None and self.operator is None


    # ========== 입력 메서드 ==========
    
    def clickNumber(self, num):
        """숫자 버튼 클릭 처리"""
        def func():
            if self._checkError():
                return
            
            # lineEdit에서 현재 숫자 읽기
            current_value = self.lineEdit.text()
            
            # operator_entered가 True이면 새로운 숫자 입력 시작
            if self.operator_entered:
                current_value = ""
            
            # 등호 후 새로운 계산 시작
            if self._isAfterEqual():
                current_value = ""
                self.accumulator = None
            
            # "-0"이면 "-"로 초기화 후 숫자 추가
            if current_value == "-0":
                current_value = "-"
            
            current_value += str(num)
            
            # 숫자 입력 후 operator_entered 플래그를 False로 설정
            self.operator_entered = False
            
            # 최종 숫자를 lineEdit에 표시
            self.render(current_value)
        return func
    
    def clickDot(self):
        """소수점 버튼 클릭 처리"""
        if self._checkError():
            return
        
        # lineEdit에서 현재 숫자 읽기
        current_value = self.lineEdit.text()
        
        # 등호 후 새로운 계산 시작
        if self._isAfterEqual():
            self.accumulator = None
        
        # 정수 패턴이면 소수점 추가
        if re.match(r'^-?\d+$', current_value):
            current_value += "."
            self.render(current_value)

    def cleanEntry(self):
        """현재 입력값만 초기화 (CE 버튼)"""
        if self._checkError():
            return

        # lineEdit의 값만 "0"으로 초기화
        # accumulator와 operator는 유지
        self.render("0")

    def cleanAll(self):
        """모든 상태 초기화 (AC 버튼)"""
        self.accumulator = None
        self.operator = None
        self.operator_entered = False
        self.has_error = False
        self.render("0")

    def render(self, value):
        """화면에 값 표시"""
        self.lineEdit.setText(value)

    # ========== 연산 메서드 ==========
    
    def _setOperator(self, operator):
        """연산자 설정 및 필요시 계산 수행"""
        if self._checkError():
            return
        
        # lineEdit의 숫자는 건드리지 않음 (화면 표시 유지)
        current_value = self.lineEdit.text()
        
        # accumulator가 없거나 비어있으면 아무것도 안함
        if self.accumulator is None:
            self.accumulator = current_value
            self.operator = operator
            self.operator_entered = True
            return

        # 이전에 operator를 눌렀다면 새로운 operator로 설정하고 종료
        if self.accumulator is not None and self.operator_entered:
            self.operator = operator
            self.operator_entered = True
            return

        # accumulator와 operator가 모두 설정되어 있고 lineEdit에 유효한 숫자가 있으면
        if self.accumulator is not None and self.operator is not None and current_value:
            # 이전 계산 수행 (accumulator 연산자 lineEdit의 숫자)
            result = self._performCalculation(self.operator, self.accumulator, current_value)
            if result is None:  # 에러 발생
                return
            # 결과를 accumulator에 저장하고 lineEdit에 표시
            self.accumulator = result
            self.render(result)
        
        
        # operator에 새로운 연산자를 저장
        self.operator = operator
        
        # operator_entered 플래그를 True로 설정
        self.operator_entered = True

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
        
        # lineEdit에서 현재 숫자 읽기
        current_value = self.lineEdit.text()
        
        # 부호 토글
        if current_value.startswith("-"):
            current_value = current_value[1:]
        else:
            current_value = "-" + current_value
        
        # lineEdit에 표시
        self.render(current_value)

    def calcEqual(self):
        """등호 버튼 - 계산 수행 및 상태 초기화"""
        if self._checkError():
            return
        
        # operator_entered가 True이면 마지막 연산자를 취소하고 현재 결과만 표시
        if self.operator_entered:
            # operator를 None으로 초기화하여 연산 취소
            self.operator = None
            # operator_entered 플래그를 False로 설정
            self.operator_entered = False
            # 현재 lineEdit의 값은 그대로 유지 (추가 계산 없음)
            return
        
        # accumulator와 operator가 모두 설정되어 있고 lineEdit에 유효한 숫자가 있을 때만 계산 수행
        current_value = self.lineEdit.text()
        if self.accumulator is not None and self.operator is not None and current_value and current_value != "ERR":
            # 계산 수행 (accumulator 연산자 lineEdit의 숫자)
            result = self._performCalculation(self.operator, self.accumulator, current_value)
            
            if result is None:  # 에러 발생
                return
            
            # 결과를 accumulator에 저장하고 lineEdit에 표시
            self.accumulator = result
            self.render(result)
            
            # operator를 None으로 초기화
            self.operator = None
            
            # operator_entered 플래그를 False로 설정
            self.operator_entered = False



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec())
