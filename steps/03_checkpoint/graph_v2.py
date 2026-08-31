from langgraph.graph import END, START, StateGraph
from . import nodes
from .state import KanbanState

def build(checkpointer=None):
    g = StateGraph(KanbanState)
    for name in ("ingest", "classify_rule", "slow_review", "to_doing", "to_backlog", "finish"):
        g.add_node(name, getattr(nodes, name))
    g.add_edge(START, "ingest")
    g.add_edge("ingest", "classify_rule")
    g.add_edge("classify_rule", "slow_review")
    g.add_conditional_edges("slow_review", nodes.route_by_decision,
                            {"to_doing": "to_doing", "to_backlog": "to_backlog"})
    g.add_edge("to_doing", "finish")
    g.add_edge("finish", END)
    g.add_edge("to_backlog", END)
    return g.compile(checkpointer=checkpointer)
