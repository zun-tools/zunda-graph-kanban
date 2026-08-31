import os
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from app.kanban import nodes
from app.kanban.state import KanbanState

# graph_v3.py の逐語コピーを土台に、承認待ちを review 列で待たせる版（回01 S1 と同型）。
# 経路: classify_rule -(urgent)-> to_review -> human_approval -> finish
# graph_v3.py は1バイトも触らない（LG12〜LG16 の証拠と langgraph.json の既存エントリが指すため）。
# langgraph dev はファイルを直接 exec するので絶対 import で書く（LG15 実測）。

def to_review(state):
    return nodes._move(state, "review", "to_review")

def human_approval(state):
    if os.environ.get("LG_APPROVAL_COUNTER"):
        nodes._append(os.environ["LG_APPROVAL_COUNTER"], "human_approval")
    print("[node] human_approval", flush=True)
    card = state["board"][-1]
    request = {
        "action_request": {"action": "move_card",
                           "args": {"id": card["id"], "title": card["title"], "to": "done"}},
        "config": {"allow_ignore": True, "allow_respond": True,
                   "allow_edit": True, "allow_accept": True},
        "description": "エージェントがこのカードを done へ動かしてよいか",
    }
    answers = interrupt([request])          # Agent Inbox は list を送り返す
    answer = answers[0] if isinstance(answers, list) else answers
    kind = answer.get("type")
    if kind in ("accept", "edit"):
        return Command(goto="finish", update={"log": [f"approved:{kind}"]})
    return Command(goto="__end__", update={"note": str(answer.get("args")), "log": [f"rejected:{kind}"]})

def build(checkpointer=None):
    g = StateGraph(KanbanState)
    g.add_node("ingest", nodes.ingest)
    g.add_node("classify_rule", nodes.classify_rule)
    g.add_node("to_review", to_review)
    g.add_node("to_backlog", nodes.to_backlog)
    g.add_node("human_approval", human_approval)
    g.add_node("finish", nodes.finish)
    g.add_edge(START, "ingest")
    g.add_edge("ingest", "classify_rule")
    g.add_conditional_edges("classify_rule", nodes.route_by_decision,
                            {"to_doing": "to_review", "to_backlog": "to_backlog"})
    g.add_edge("to_review", "human_approval")
    g.add_edge("finish", END)
    g.add_edge("to_backlog", END)
    return g.compile(checkpointer=checkpointer)

graph = build()          # ← langgraph.json の "kanban_review" が指すのはこちら（checkpointer なし）
