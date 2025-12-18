# core/ranges_3bet.py
from typing import List
from core.enums import Position, POSITIONS
from core.utils_hand import is_pocket
from core.ranges_open import in_open_range
from core.ranks import RANK_TO_STR


def hero_is_blind(hero_pos: Position) -> bool:
    # 今回は UTG〜BTN だけを前提にするので常に False 扱い
    return False


def rank_is(hi: int, lo: int, rank: int) -> bool:
    return (hi == rank and lo != rank) or (lo == rank and hi != rank)


def is_Ax(hi: int, lo: int) -> bool:
    return 14 in (hi, lo) and hi != lo


def hand_matches(hi: int, lo: int, suited: bool, pattern: str) -> bool:
    """
    パターン文字列（例: 'QQ+', 'AKo', 'AKs', 'A5s' など）とマッチするかを簡易判定。
    """
    # ポケット QQ+ など
    if pattern.endswith("+") and len(pattern) == 3 and pattern[0] == pattern[1]:
        base_rank_char = pattern[0]
        base_rank = [k for k, v in RANK_TO_STR.items() if v == base_rank_char][0]
        if is_pocket(hi, lo) and hi >= base_rank:
            return True
        return False

    # AKo / AKs / A5s など
    if len(pattern) == 3:
        r1, r2, s = pattern[0], pattern[1], pattern[2]
        rank1 = [k for k, v in RANK_TO_STR.items() if v == r1][0]
        rank2 = [k for k, v in RANK_TO_STR.items() if v == r2][0]

        # ペアではないこと前提の2枚
        if hi == rank1 and lo == rank2:
            if s == "s" and suited:
                return True
            if s == "o" and not suited:
                return True
        return False

    return False


def three_bet_allowed_actions(
    hero_pos: Position, villain_pos: Position, hi: int, lo: int, suited: bool
) -> List[str]:
    """
    3betスポットで自分ルール上「許容されるアクション」のリストを返す。
    ['3bet'], ['call'], ['3bet', 'call'], ['3bet', 'fold'] など。
    """
    # デフォルトは「foldのみ許容」
    actions = {"fold"}

    # ブラインド以外では QQ+, AKo, AKs は必ず3bet
    if not hero_is_blind(hero_pos):
        if (
            hand_matches(hi, lo, suited, "QQ+")
            or hand_matches(hi, lo, suited, "AKo")
            or hand_matches(hi, lo, suited, "AKs")
        ):
            return ["3bet"]

    # オープンが UTG / UTG+1 / UTG+2 のときの特別ルール
    if villain_pos in (Position.UTG, Position.UTG1, Position.UTG2):
        # 必ず3bet: AKo, QQ+, AQs+
        if (
            hand_matches(hi, lo, suited, "AKo")
            or hand_matches(hi, lo, suited, "QQ+")
            or hand_matches(hi, lo, suited, "AQs")
        ):
            return ["3bet"]

        # 必ずcold call: AJs, 88, 99
        if hand_matches(hi, lo, suited, "AJs"):
            return ["call"]
        if is_pocket(hi, lo) and hi in (8, 9):
            return ["call"]

        # call or 3bet: TT, JJ, KQs
        if is_pocket(hi, lo) and hi in (10, 11):
            actions = {"3bet", "call"}
        if hand_matches(hi, lo, suited, "KQs"):
            actions = {"3bet", "call"}

        # 3bet or fold: A5s
        if hand_matches(hi, lo, suited, "A5s"):
            actions = {"3bet", "fold"}

        return sorted(actions)

    # それ以外のポジションのオープンに対して：
    # 「一つ上の行」のオープンレンジに入っていれば 3bet or call
    order = POSITIONS
    v_idx = order.index(villain_pos)

    # 「行」の概念に合わせたいので、UTG1/UTG2 は UTG1 の上に UTG、
    # LJ/HJ は LJ の上に UTG2 という感じで近似。
    if v_idx > 0:
        upper_pos = order[v_idx - 1]
    else:
        upper_pos = Position.UTG

    if in_open_range(upper_pos, hi, lo, suited):
        actions = {"3bet", "call"}
    else:
        actions = {"fold"}

    return sorted(actions)
