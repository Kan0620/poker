# core/enums.py
from enum import Enum
from typing import Tuple

# ==========
# 型定義
# ==========

# カード表現: (rank, suit) のタプル
# 例: (14, 's') = As, (13, 'h') = Kh
Card = Tuple[int, str]


# ==========
# Enum定義
# ==========

class StudyMode(str, Enum):
    OPEN_RANGE = "open_range"
    SB_OPEN = "sb_open"
    THREE_BET = "three_bet"
    THREE_BET_DEFENCE = "three_bet_defence"
    POWER_NUMBER = "power_number"
    BB_DEFENCE = "bb_defence"
    MDF_TRAINER = "mdf_trainer"
    MIX = "mix"


class Position(str, Enum):
    UTG = "UTG"
    UTG1 = "UTG+1"
    UTG2 = "UTG+2"
    LJ = "LJ"
    HJ = "HJ"
    CO = "CO"
    BTN = "BTN"
    SB = "SB"
    BB = "BB"


# バケット定義（強い順）
class Bucket(str, Enum):
    MONSTER = "Monster"
    STRONG_MADE = "Strong Made"
    WEAK_MADE = "Weak Made"
    DRAW = "Draw"
    SD_VALUE = "SD Value"
    AIR = "Air"


# ==========
# 定数
# ==========

# バケット順序（強い順）
BUCKET_ORDER = [
    Bucket.MONSTER,
    Bucket.STRONG_MADE,
    Bucket.WEAK_MADE,
    Bucket.DRAW,
    Bucket.SD_VALUE,
    Bucket.AIR,
]

# ポジション定義
POSITIONS = [
    Position.UTG,
    Position.UTG1,
    Position.UTG2,
    Position.LJ,
    Position.HJ,
    Position.CO,
    Position.BTN,
]

POSITIONS_WITH_SB = POSITIONS + [Position.SB]
