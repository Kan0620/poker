# core/ranges_3bet_defence.py
from core.enums import Position
from core.utils_hand import is_pocket
from core.ranges_open import in_utg12_open_range


def is_in_utg12_defence_core(hi: int, lo: int, suited: bool) -> bool:
    """"UTG+1/2オープンレンジに入るか"を再利用（ベースディフェンスレンジ）"""
    return in_utg12_open_range(hi, lo, suited)


def defend_vs_ip_3bet(hi: int, lo: int, suited: bool) -> bool:
    """
    相手がIP側（自分がOOP）から3betしてきたときに defend するか。
    - オフスートは AQo+ だけ
    - スーテッドAXは AJs+, A5s
    - ポケットは 77+
    """
    # ポケット
    if is_pocket(hi, lo):
        return hi >= 7

    if suited:
        # AXs
        if hi == 14:
            # AJs+ or A5s
            if lo >= 11:
                return True
            if lo == 5:
                return True
        return False
    else:
        # オフスート AQo+
        if hi == 14 and lo >= 12:  # AQ, AK
            return True
        return False


def three_bet_defence_action(
    hero_pos: Position,
    in_position: bool,
    hi: int,
    lo: int,
    suited: bool,
) -> str:
    """
    3betディフェンスで 'defend' or 'fold' を返す。
    """
    # まず「UTG+1/2オープンレンジに入っているか」でフィルタ
    if not is_in_utg12_defence_core(hi, lo, suited):
        return "fold"

    # 自分がOOP（相手がIPから3bet）のときはタイトに
    if not in_position:
        return "defend" if defend_vs_ip_3bet(hi, lo, suited) else "fold"

    # 自分がIP（相手OOPから3bet）のときは UTG+1/2レンジ内は全部defend
    return "defend"
