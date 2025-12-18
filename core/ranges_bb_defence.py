# core/ranges_bb_defence.py
from core.enums import Position
from core.utils_hand import is_pocket


def bb_defence_vs_open(villain_pos: Position, hi: int, lo: int, suited: bool) -> bool:
    """
    BBでVillainのオープンに対して defend(call) するか / fold するか。
    """
    # vs UTG
    if villain_pos == Position.UTG:
        # ポケット：66+
        if is_pocket(hi, lo):
            return hi >= 6

        if not suited:
            # Offsuit: AQo+ (Axo where x≥12)
            if hi == 14 and lo >= 12:
                return True
            return False
        else:
            # Suited Axs: ATs+
            if hi == 14 and lo >= 10:
                return True
            # Suited 両方≥11
            if hi >= 11 and lo >= 11:
                return True
            # Suited コネ: 下≥7 & gap≤1
            if lo >= 7 and (hi - lo) <= 1:
                return True
            return False

    # vs UTG+1 / UTG+2
    if villain_pos in (Position.UTG1, Position.UTG2):
        # ポケット：55+
        if is_pocket(hi, lo):
            return hi >= 5

        if not suited:
            # Offsuit: AJo+ + 両方≥12
            if hi == 14 and lo >= 11:  # AJo+
                return True
            if hi >= 12 and lo >= 12:  # QQ+ は pocket でカバー済みなので実質 KQ, KJ, QJ など
                return True
            return False
        else:
            # Suited Axs: 全部
            if hi == 14:
                return True
            # Suited 両方≥10
            if hi >= 10 and lo >= 10:
                return True
            # Suited コネ: 下≥6 & gap≤1
            if lo >= 6 and (hi - lo) <= 1:
                return True
            return False

    # vs LJ / HJ
    if villain_pos in (Position.LJ, Position.HJ):
        # ポケット：22+ (全部)
        if is_pocket(hi, lo):
            return True

        if not suited:
            # Offsuit: ATo+ + 両方≥11
            if hi == 14 and lo >= 10:
                return True
            if hi >= 11 and lo >= 11:
                return True
            return False
        else:
            # Suited Axs: 全部
            if hi == 14:
                return True
            # Suited 両方≥8
            if hi >= 8 and lo >= 8:
                return True
            # Suited コネ/ギャッパ: 下≥4 & gap≤2
            if lo >= 4 and (hi - lo) <= 2:
                return True
            return False

    # vs CO / BTN
    if villain_pos in (Position.CO, Position.BTN):
        # ポケット：22+ (全部)
        if is_pocket(hi, lo):
            return True

        if not suited:
            # Offsuit: A8o+ + 両方≥10
            if hi == 14 and lo >= 8:
                return True
            if hi >= 10 and lo >= 10:
                return True
            return False
        else:
            # Suited Axs: 全部
            if hi == 14:
                return True
            # Suited 両方≥7
            if hi >= 7 and lo >= 7:
                return True
            # Suited コネ/ギャッパ: 下≥4 & gap≤2
            if lo >= 4 and (hi - lo) <= 2:
                return True
            return False

    return False
