"""第04話（Send fanout）— LG17（n=7）と同じ入力を graph_v4.build() に流すだけの実行入口。
新しいロジックはここに書かない。
"""
from __future__ import annotations
import json

from app.kanban.graph_v4 import build

graph = build()


def main() -> None:
    n = 7
    inbox = [f"依頼{i}" for i in range(1, n + 1)]
    result = graph.invoke({"inbox": inbox, "board": []})
    print("[result]", json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
