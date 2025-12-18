# core/cards.py
import random
from typing import List, Tuple
from itertools import combinations
from core.enums import Card
from core.ranks import RANK_TO_STR


# スート定義（MDFモード用）
SUITS = ["s", "h", "d", "c"]  # spade, heart, diamond, club

# スート絵文字マッピング
SUIT_EMOJI = {
    "s": "♠️",  # spade
    "h": "♥️",  # heart
    "d": "♦️",  # diamond
    "c": "♣️",  # club
}


def card_to_str(card: Card) -> str:
    """カードを文字列表現に変換（例: A♠️, K♥️）"""
    rank, suit = card
    return f"{RANK_TO_STR[rank]}{SUIT_EMOJI[suit]}"


def generate_board() -> List[Card]:
    """ランダムにフロップ3枚を生成"""
    all_cards = [(r, s) for r in RANK_TO_STR.keys() for s in SUITS]
    return random.sample(all_cards, 3)


def enumerate_all_combos() -> List[Tuple[Card, Card]]:
    """全1326コンボを列挙"""
    all_cards = [(r, s) for r in RANK_TO_STR.keys() for s in SUITS]
    return list(combinations(all_cards, 2))


def combo_to_hand_type(c1: Card, c2: Card) -> Tuple[int, int, bool]:
    """コンボ (card1, card2) を (hi, lo, suited) に変換"""
    r1, s1 = c1
    r2, s2 = c2
    hi = max(r1, r2)
    lo = min(r1, r2)
    suited = (s1 == s2) and (r1 != r2)
    return hi, lo, suited


def blocks_with_board(combo: Tuple[Card, Card], board: List[Card]) -> bool:
    """コンボがボードとカードが被るかチェック"""
    c1, c2 = combo
    board_set = set(board)
    return c1 in board_set or c2 in board_set
