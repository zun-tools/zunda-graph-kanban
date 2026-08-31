"""第03話（human_approval / interrupt）— LG12c と同じ入力で graph_v3b を止め、
停止点の column を出すだけの実行入口。新しいロジックはここに書かない。
"""
from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver

from app.kanban.graph_v3b import build


def main() -> None:
    checkpointer = InMemorySaver()
    graph = build(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "ep03-1"}}
    result = graph.invoke({"inbox": ["bug: 締切表示がずれる"], "board": []}, config=config)
    state = graph.get_state(config)
    board = state.values.get("board", [])
    board_column = board[-1].get("column") if board else None
    print("[invoke result]", result)
    print("[next]", list(state.next))
    print("[board column]", board_column)


if __name__ == "__main__":
    main()
