from __future__ import annotations
import os
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from . import nodes
from .state import KanbanState
from .nodes import _append


def fan_out(state):                      # 実行時に個数が決まる
    return [Send("review_one", {"title": t}) for t in state["inbox"]]

def review_one(payload):                 # 並列枝。合流先は reducer 付きの results だけ
    if os.environ.get("LG_FANOUT_COUNTER"):
        _append(os.environ["LG_FANOUT_COUNTER"], "review_one")
    return {"results": [f"reviewed:{payload['title']}"], "log": ["review_one"]}

def collect(state):
    return {"log": ["collect"]}

# --- LG17: Send による実行時ファンアウト（結果は operator.add で合流） ---
def build(checkpointer=None):
    g = StateGraph(KanbanState)
    g.add_node("review_one", review_one)
    g.add_node("collect", collect)
    g.add_conditional_edges(START, fan_out)
    g.add_edge("review_one", "collect")
    g.add_edge("collect", END)
    return g.compile(checkpointer=checkpointer)


# --- LG18: subgraph（カード1枚の詳細レビュー、2 node）。checkpointer は渡さない ---
# 注記: fan_out（Send）で作った operator.add reducer の枝に「直結」で subgraph を繋ぐと、
# 実測で reducer の集計が二重になる現象が観測された（review_one の副作用カウンタは
# n 回のままなのに results/collect の適用が2回起きる）。原因は未特定（LangGraph 側の
# pending writes 再適用のタイミングか、こちらの繋ぎ方の問題かを切り分けられていない）。
# LG17（Send の実測）と LG18（subgraph 継承の実測）を同じ主張として汚さないよう、
# subgraph は fan-out 経路とは独立した入口から呼ぶ構成に分離した。
def sub_step1(state):
    return {"log": ["sub_step1"]}

def sub_step2(state):
    return {"log": ["sub_step2"], "note": "reviewed-by-subgraph"}

def build_subgraph():
    sg = StateGraph(KanbanState)
    sg.add_node("sub_step1", sub_step1)
    sg.add_node("sub_step2", sub_step2)
    sg.add_edge(START, "sub_step1")
    sg.add_edge("sub_step1", "sub_step2")
    sg.add_edge("sub_step2", END)
    return sg.compile()   # checkpointer なし＝親から引き継ぐ

def build_with_subgraph(checkpointer=None):
    g = StateGraph(KanbanState)
    g.add_node("ingest", nodes.ingest)
    g.add_node("card_review", build_subgraph())
    g.add_edge(START, "ingest")
    g.add_edge("ingest", "card_review")
    g.add_edge("card_review", END)
    return g.compile(checkpointer=checkpointer)
