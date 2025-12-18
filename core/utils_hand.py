# core/utils_hand.py
import random
from typing import Tuple
from core.ranks import RANK_TO_STR


def hand_label(hi: int, lo: int, suited: bool) -> str:
    # ペアは "TT" などで表示
    if hi == lo:
        return f"{RANK_TO_STR[hi]}{RANK_TO_STR[lo]}"
    s = "s" if suited else "o"
    return f"{RANK_TO_STR[hi]}{RANK_TO_STR[lo]}{s}"


def random_hand() -> Tuple[int, int, bool]:
    """ランダムなハンド（hi, lo, suited）を返す。"""
    ranks = list(RANK_TO_STR.keys())
    hi = random.choice(ranks)
    lo = random.choice(ranks)
    if lo > hi:
        hi, lo = lo, hi
    suited = (hi != lo) and (random.random() < 0.5)
    return hi, lo, suited


def is_pocket(hi: int, lo: int) -> bool:
    return hi == lo


def is_broadway(rank: int) -> bool:
    return rank >= 10  # T, J, Q, K, A
