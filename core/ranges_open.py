# core/ranges_open.py
from core.enums import Position
from core.utils_hand import is_pocket, is_broadway


def in_utg_open_range(hi: int, lo: int, suited: bool) -> bool:
    # ポケット
    if is_pocket(hi, lo):
        return hi >= 8
    total = hi + lo
    if not suited:
        # O: 足して26以上
        return total >= 26
    else:
        # S: 強い系 足して24以上
        return total >= 24


def in_utg12_open_range(hi: int, lo: int, suited: bool) -> bool:
    """
    UTG+1 / UTG+2 共通のオープンレンジ
    """
    # ポケット
    if is_pocket(hi, lo):
        return hi >= 5
    total = hi + lo
    if not suited:
        # O: 足して25以上
        return total >= 25
    else:
        # S: 強い系 BWs, A9s以上, A4s, A5s
        if hi == 14:
            # A9s+
            if lo >= 9:
                return True
            # A4s, A5s
            if lo in (4, 5):
                return True
        # BWs（ブロードウェイスーテッド）
        if is_broadway(hi) and is_broadway(lo):
            return True
        return False


def in_hjlj_open_range(hi: int, lo: int, suited: bool) -> bool:
    """
    LJ / HJ 共通のオープンレンジ
    """
    # ポケット：全部
    if is_pocket(hi, lo):
        return True

    total = hi + lo
    if not suited:
        # O: 足して23以上
        return total >= 23
    else:
        # S: 強い系 AXs, KXs
        if hi in (14, 13):
            return True
        # S: 両方x以上 (x=8)
        if hi >= 8 and lo >= 8:
            return True
        return False


def in_co_open_range(hi: int, lo: int, suited: bool) -> bool:
    # ポケット：全部
    if is_pocket(hi, lo):
        return True

    if not suited:
        # O: 9以上, Ax(x≧8)
        if hi >= 9 and lo >= 9:
            return True
        if hi == 14 and lo >= 8:
            return True
        return False
    else:
        # S: 強い系 A〜QXs
        if hi in (14, 13, 12):
            return True
        # S: 両方x以上 (x=7)
        if hi >= 7 and lo >= 7:
            return True
        # S: コネ/ギャッパ 45s以上
        if lo >= 4 and (hi - lo) <= 3:
            return True
        return False


def in_btn_open_range(hi: int, lo: int, suited: bool) -> bool:
    # ポケット：全部
    if is_pocket(hi, lo):
        return True

    if not suited:
        # O: 両方x以上, Ax (x=8)
        if hi >= 8 and lo >= 8:
            return True
        if hi == 14:
            return True  # Axo全部
        return False
    else:
        # S: 強い系 A〜TXs
        if hi >= 10:
            return True
        # S: 両方x以上 (x=5)
        if hi >= 5 and lo >= 5:
            return True
        # S: コネ/ギャッパ 45s, 46s以上
        if lo >= 4 and (hi - lo) <= 2:
            return True
        return False


def in_open_range(pos: Position, hi: int, lo: int, suited: bool) -> bool:
    if pos == Position.UTG:
        return in_utg_open_range(hi, lo, suited)
    elif pos in (Position.UTG1, Position.UTG2):
        return in_utg12_open_range(hi, lo, suited)
    elif pos in (Position.LJ, Position.HJ):
        return in_hjlj_open_range(hi, lo, suited)
    elif pos == Position.CO:
        return in_co_open_range(hi, lo, suited)
    elif pos == Position.BTN:
        return in_btn_open_range(hi, lo, suited)
    return False
