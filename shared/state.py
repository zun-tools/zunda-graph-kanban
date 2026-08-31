from __future__ import annotations
import operator
from typing import Annotated, TypedDict

Card = TypedDict("Card", {"id": str, "title": str, "column": str, "owner": str})

class KanbanState(TypedDict, total=False):
    inbox: list[str]                              # 未処理の依頼文
    board: list[Card]                             # 板の現在値（reducer 無し＝上書き）
    decision: str                                 # 条件分岐の判定
    note: str                                     # 差し戻し理由など
    results: Annotated[list[str], operator.add]   # 並列枝の合流先（LG17）
    log: Annotated[list[str], operator.add]       # 通った node の記録
