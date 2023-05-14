from enum import Enum

class C(Enum):
    Null = 0
    Arithmetic = 1
    Push = 2
    Pop = 3
    Label = 4
    Goto = 5
    IfGoto = 6
    Function = 7
    Return = 8
    Call = 9