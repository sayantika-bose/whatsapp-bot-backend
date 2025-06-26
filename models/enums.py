from enum import Enum

class AgeGroupEnum(str, Enum):
    AGE_18_25 = "18-25"
    AGE_26_35 = "26-35"
    AGE_36_49  = "36-49"
    AGE_50_PLUS = "50+"

class AnswerLabel(str, Enum):
    a = 'A'
    b = 'B'
    c = 'C'
    d = 'D'

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"