from langgraph.graph import StateGraph, START, END
from graph.state import WorkflowState
from graph.nodes import analyze_content, generate_draft

def build_basic_graph():

    """
    Build a minimal LangGraph workflow:

        START → analyze_content → generate_draft → END
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("analyze_content", analyze_content)
    graph.add_node("generate_draft", generate_draft)

    graph.add_edge(START, "analyze_content")
    graph.add_edge("analyze_content", "generate_draft")
    graph.add_edge("generate_draft", END)

    return graph.compile()