from __future__ import annotations
import os, time
from .state import KanbanState

def _mark(name: str) -> str:
    return f"{name}@pid{os.getpid()}"

def _append(path: str, name: str) -> None:      # 副作用カウンタ（再実行の有無を測る）
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{name}\tpid={os.getpid()}\t{time.time():.3f}\n")

def ingest(state: KanbanState) -> dict:
    inbox = list(state.get("inbox", []))
    board = list(state.get("board", []))
    title = inbox.pop(0)
    board.append({"id": f"c{len(board) + 1}", "title": title, "column": "todo", "owner": "agent"})
    if os.environ.get("LG_INGEST_COUNTER"):
        _append(os.environ["LG_INGEST_COUNTER"], "ingest")
    print(f"[node] ingest title={title!r}", flush=True)
    return {"inbox": inbox, "board": board, "log": [_mark("ingest")]}

def classify_rule(state: KanbanState) -> dict:
    decision = "urgent" if "bug" in state["board"][-1]["title"].lower() else "normal"
    print(f"[node] classify_rule decision={decision}", flush=True)
    return {"decision": decision, "log": [_mark("classify_rule")]}

def route_by_decision(state: KanbanState) -> str:
    return "to_doing" if state.get("decision") == "urgent" else "to_backlog"

def _move(state: KanbanState, column: str, node: str) -> dict:
    board = [dict(c) for c in state.get("board", [])]
    board[-1]["column"] = column
    print(f"[node] {node} column={column}", flush=True)
    return {"board": board, "log": [_mark(node)]}

def to_doing(state):   return _move(state, "doing", "to_doing")
def to_backlog(state): return _move(state, "backlog", "to_backlog")
def finish(state):     return _move(state, "done", "finish")

def slow_review(state: KanbanState) -> dict:
    """LG10 用。LG_SLOW_SECONDS 秒眠り、開始マーカーを置く（既定 0 秒＝他の試行に影響しない）。"""
    if os.environ.get("LG_SLOW_COUNTER"):
        _append(os.environ["LG_SLOW_COUNTER"], "slow_review")
    if os.environ.get("LG_SLOW_MARKER"):
        open(os.environ["LG_SLOW_MARKER"], "a", encoding="utf-8").write(f"start pid={os.getpid()}\n")
    time.sleep(float(os.environ.get("LG_SLOW_SECONDS", "0")))
    print("[node] slow_review done", flush=True)
    return {"log": [_mark("slow_review")]}
