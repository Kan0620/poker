# core/ranges_sb_open.py
from core.ranges_open import in_btn_open_range


def sb_first_in_action(hi: int, lo: int, suited: bool) -> str:
    """
    SB first-in（全員フォールド）での RAISE / LIMP / FOLD を返す。
    ルール：
    1. BTNオープンレンジに入るなら RAISE
    2. それ以外でオフスートなら FOLD
    3. それ以外（スーテッド）で下が3以下なら FOLD（ただしA3s/A2sはBTNレンジでRAISEなので除外済み）
    4. 上記以外の残りスーテッドは LIMP
    """
    # 1. BTNオープンレンジに入るなら RAISE
    if in_btn_open_range(hi, lo, suited):
        return "raise"

    # 2. オフスートは FOLD
    if not suited:
        return "fold"

    # 3. スーテッドで下が3以下なら FOLD
    if lo <= 3:
        return "fold"

    # 4. 残りのスーテッドは LIMP
    return "limp"
