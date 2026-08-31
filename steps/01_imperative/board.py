from __future__ import annotations


def run(inbox: list[str]) -> dict:
    """LangGraph を import せず、graph_v1 と同じ最終 board を返す素の while ループ実装。"""
    inbox = list(inbox)
    board: list[dict] = []
    log: list[str] = []
    while inbox:
        title = inbox.pop(0)
        board.append({"id": f"c{len(board) + 1}", "title": title, "column": "todo", "owner": "agent"})
        print(f"[node] ingest title={title!r}", flush=True)

        decision = "urgent" if "bug" in board[-1]["title"].lower() else "normal"
        print(f"[node] classify_rule decision={decision}", flush=True)

        if decision == "urgent":
            board[-1]["column"] = "doing"
            print(f"[node] to_doing column=doing", flush=True)
            board[-1]["column"] = "done"
            print(f"[node] finish column=done", flush=True)
        else:
            board[-1]["column"] = "backlog"
            print(f"[node] to_backlog column=backlog", flush=True)

    return {"inbox": inbox, "board": board, "log": log}
