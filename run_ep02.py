"""第02話（checkpointer）— LG08b と同じ入力・同じ「新規 thread・1周だけ」で
history 件数を出すだけの実行入口。新しいロジックはここに書かない。
"""
from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver

from app.kanban.graph_v2 import build


def main() -> None:
    checkpointer = InMemorySaver()
    graph = build(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "ep02-1"}}
    result = graph.invoke({"inbox": ["改善案: サイドバーを広げたい"], "board": []}, config=config)
    history = list(graph.get_state_history(config))
    print("[invoke result]", result)
    print("[history len]", len(history))


if __name__ == "__main__":
    main()
