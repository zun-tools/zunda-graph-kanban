from __future__ import annotations
import os
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from .state import KanbanState
from .nodes import _append


def fan_out(state):
    return [Send("review_one_conflict", {"title": t}) for t in state["inbox"]]

def review_one_conflict(payload):
    _append(os.environ["LG_FANOUT_COUNTER"], "review_one_conflict")
    # reducer の無い board へ並列書き込み＝期待失敗
    return {"board": [{"id": "x", "title": payload["title"], "column": "todo", "owner": "agent"}]}

def build():
    g = StateGraph(KanbanState)
    g.add_node("review_one_conflict", review_one_conflict)
    g.add_conditional_edges(START, fan_out, ["review_one_conflict"])
    g.add_edge("review_one_conflict", END)
    return g.compile()
