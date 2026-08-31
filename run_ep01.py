"""第01話（StateGraph）— LG03 と同じ入力を graph_v1 に流すだけの実行入口。
新しいロジックはここに書かない。グラフを呼ぶだけ。
"""
from __future__ import annotations
import json

from app.kanban.graph_v1 import graph


def main() -> None:
    urgent = graph.invoke({"inbox": ["bug: 締切表示がずれる"], "board": []})
    normal = graph.invoke({"inbox": ["改善案: サイドバーを広げたい"], "board": []})
    print("[urgent]", json.dumps(urgent, ensure_ascii=False))
    print("[normal]", json.dumps(normal, ensure_ascii=False))


if __name__ == "__main__":
    main()
