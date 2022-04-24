from enum import Enum

class GenDirection(Enum):
    HORIZONAL = 0
    BIDIRECTIONAL = 1

class GenMethod(Enum):
    SUBBLOCK_RANDOM = 1
    SUBBLOCK_ROW = 2
    GLOBAL_ROW = 3