# core/power_number.py
from core.enums import Position
from core.utils_hand import is_pocket
from core.ranges_open import (
    in_utg_open_range,
    in_utg12_open_range,
    in_hjlj_open_range,
    in_co_open_range,
    in_btn_open_range,
)
from core.ranks import RANK_TO_STR


def assign_power_number(hero_pos: Position, hi: int, lo: int, suited: bool) -> int:
    """
    自作PNルール：
      - UTGオープンレンジ → 999（∞扱い）
      - そこになくUTG+1/2レンジ（A4s, A5s除外）→ 50
      - そこまでになくHJ/LJレンジ内：
          - KXs かつ X<=8 → 9+X
          - それ以外 → 20
      - そこまでになくCOレンジ → 10
      - そこまでになくBTNレンジ + KXo + QXo → 5
      - それ以外 → 0（常にフォールド）
    """
    # まずUTGオープンレンジ
    if in_utg_open_range(hi, lo, suited):
        return 999

    # UTG+1/2（A4s, A5s除外）
    if in_utg12_open_range(hi, lo, suited):
        if not (suited and hi == 14 and lo in (4, 5)):
            return 50

    # HJ/LJ
    if in_hjlj_open_range(hi, lo, suited):
        # KXs で X<=8
        if suited and hi == 13 and lo <= 8:
            return 9 + lo
        return 20

    # CO
    if in_co_open_range(hi, lo, suited):
        return 10

    # BTN or KXo/QXo
    if in_btn_open_range(hi, lo, suited):
        return 5

    # KXo or QXo （どのレンジにも入ってない＋オフスート）
    if not suited and not is_pocket(hi, lo):
        hi_char = RANK_TO_STR[hi]
        if hi_char in ("K", "Q"):
            return 5

    return 0


def players_behind(pos: Position) -> int:
    """
    各ポジションごとの「後ろにいるプレイヤー数」を明示的に定義する。
    9-handed 想定：

      UTG   → UTG+1, UTG+2, LJ, HJ, CO, BTN, SB, BB  = 8
      UTG+1 → UTG+2, LJ, HJ, CO, BTN, SB, BB         = 7
      UTG+2 → LJ, HJ, CO, BTN, SB, BB                = 6
      LJ    → HJ, CO, BTN, SB, BB                    = 5
      HJ    → CO, BTN, SB, BB                        = 4
      CO    → BTN, SB, BB                            = 3
      BTN   → SB, BB                                 = 2
    """
    mapping = {
        Position.UTG: 8,
        Position.UTG1: 7,
        Position.UTG2: 6,
        Position.LJ: 5,
        Position.HJ: 4,
        Position.CO: 3,
        Position.BTN: 2,
        Position.SB: 1,
        Position.BB: 0,
    }
    return mapping[pos]


def should_shove_with_power_number(
    hero_pos: Position, hi: int, lo: int, suited: bool, m_value: float
) -> bool:
    """
    M値 < 6 前提で、PN × 後ろ人数 と M × 後ろ人数 を比較して shove or fold を決める。
    """
    if m_value >= 6:
        return False

    pn = assign_power_number(hero_pos, hi, lo, suited)
    if pn <= 0:
        return False

    behind = players_behind(hero_pos)
    threshold = m_value * behind
    return pn >= threshold
