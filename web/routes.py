# web/routes.py
from typing import Optional, List
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.enums import StudyMode
from core.utils_hand import hand_label
from core.cards import card_to_str
from core.range_combos import get_range_combos
from mdf.analysis import calculate_mdf_analysis
from quiz.generators import generate_question

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    mode: str = StudyMode.OPEN_RANGE.value,
    # 問題復元用パラメータ
    q_mode: Optional[str] = None,
    hero_pos: Optional[str] = None,
    villain_pos: Optional[str] = None,
    hand_hi: Optional[int] = None,
    hand_lo: Optional[int] = None,
    suited: Optional[str] = None,
    m_value: Optional[float] = None,
    in_position: Optional[str] = None,
    correct_action: Optional[str] = None,
    # MDF用復元パラメータ
    range_name: Optional[str] = None,
    board: Optional[str] = None,
    bet_size: Optional[float] = None,
):
    try:
        ui_mode = StudyMode(mode)
    except ValueError:
        ui_mode = StudyMode.OPEN_RANGE

    # URLパラメータから問題を復元するか、新規生成するか
    if q_mode is not None:
        # 問題復元モード
        question = {
            "mode": q_mode,
            "hero_pos": hero_pos or "",
            "villain_pos": villain_pos or "",
            "hand_hi": hand_hi or 0,
            "hand_lo": hand_lo or 0,
            "suited": (suited == "true"),
            "hand_label": hand_label(hand_hi, hand_lo, suited == "true") if hand_hi and hand_lo else "",
            "m_value": m_value,
            "in_position": (in_position == "true") if in_position else None,
            "correct_action": correct_action or "",
        }

        # MDFモードの場合、追加データを復元
        if q_mode == StudyMode.MDF_TRAINER.value and range_name and board and bet_size is not None:
            # ボードを表示用に変換
            board_cards_str = board.split(',')
            board_display = []
            board_cards = []
            for card_str in board_cards_str:
                suit_str = card_str[-1]
                rank_str = card_str[:-1]
                rank = int(rank_str)
                board_cards.append((rank, suit_str))
                board_display.append(card_to_str((rank, suit_str)))

            # MDF分析を実行
            range_combos = get_range_combos(range_name)
            analysis = calculate_mdf_analysis(range_combos, board_cards, bet_size)

            question.update({
                "range_name": range_name,
                "board": board_display,
                "board_raw": board,
                "bet_size": bet_size,
                "analysis": analysis,
            })
    else:
        # 新規問題生成
        question = generate_question(ui_mode)

    context = {
        "request": request,
        "study_modes": list(StudyMode),
        "ui_mode": ui_mode.value,
        "question": question,
        "last_result": None,
    }
    return templates.TemplateResponse("index.html", context)


@router.post("/answer", response_class=HTMLResponse)
async def answer(
    request: Request,
    mode: str = Form(...),              # 出題時の question.mode
    requested_mode: str = Form(...),    # UIで選んだモード（mix含む）
    correct_action: str = Form(...),
    hero_pos: str = Form(""),
    villain_pos: str = Form(""),
    hand_hi: int = Form(0),
    hand_lo: int = Form(0),
    suited: str = Form("false"),
    m_value: Optional[float] = Form(None),
    in_position: Optional[str] = Form(None),
    user_action: Optional[str] = Form(None),
    user_actions: Optional[List[str]] = Form(None),
    # MDF用パラメータ
    range_name: Optional[str] = Form(None),
    board: Optional[str] = Form(None),
    bet_size: Optional[float] = Form(None),
):
    hi = int(hand_hi)
    lo = int(hand_lo)
    is_suited = (suited == "true")

    hero_position = hero_pos
    villain_position = villain_pos or None

    # in_position は three_bet_defence 以外は None
    if in_position is not None and in_position != "":
        in_pos_bool = (in_position == "true")
    else:
        in_pos_bool = None

    # 正解アクション側（文字列）
    expected_raw = correct_action

    # ユーザーの回答解析
    if mode == StudyMode.THREE_BET.value:
        # チェックボックス: user_actions で複数選択
        user_actions_list = user_actions or []
        user_set = set(user_actions_list)

        expected_set = set()
        if expected_raw:
            for token in expected_raw.split(","):
                token = token.strip()
                if token:
                    expected_set.add(token)

        is_correct = (user_set == expected_set)
        user_action_str = ",".join(sorted(user_set)) if user_set else "(none)"
        expected_str = ",".join(sorted(expected_set))
    else:
        # ラジオボタン
        ua = user_action or ""
        is_correct = (ua == expected_raw)
        user_action_str = ua
        expected_str = expected_raw

    # 前問の結果を構築
    last_result = {
        "is_correct": is_correct,
        "mode": mode,
        "hand_label": hand_label(hi, lo, is_suited) if hi > 0 else "",
        "hero_pos": hero_position,
        "villain_pos": villain_position,
        "m_value": m_value,
        "in_position": in_pos_bool,
        "user_action": user_action_str,
        "expected": expected_str,
    }

    # MDFモードの場合、追加データを含める
    if mode == StudyMode.MDF_TRAINER.value and range_name and board and bet_size is not None:
        # ボード文字列をパース
        board_cards_str = board.split(',')
        # 分析を再実行（答え合わせ用）
        range_combos = get_range_combos(range_name)
        # ボードを再構築
        board_cards = []
        for card_str in board_cards_str:
            # card_str format: "14s" or "2c" (rank + suit)
            suit_str = card_str[-1]  # 最後の文字がスート
            rank_str = card_str[:-1]  # それ以外がランク（数値文字列）
            rank = int(rank_str)
            board_cards.append((rank, suit_str))

        analysis = calculate_mdf_analysis(range_combos, board_cards, bet_size)

        last_result.update({
            "range_name": range_name,
            "board": board,
            "bet_size": bet_size,
            "analysis": analysis,
        })

    # 次の問題を生成（UIで選んだモードに基づく）
    try:
        ui_mode = StudyMode(requested_mode)
    except ValueError:
        ui_mode = StudyMode.OPEN_RANGE

    next_question = generate_question(ui_mode)

    context = {
        "request": request,
        "study_modes": list(StudyMode),
        "ui_mode": ui_mode.value,
        "question": next_question,
        "last_result": last_result,
    }
    return templates.TemplateResponse("index.html", context)
