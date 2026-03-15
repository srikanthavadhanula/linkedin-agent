from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import WorkflowState
from graph.nodes import (
    analyze_content,
    research_online,
    generate_draft,
    review_draft,
    decide_next_step,
    revise_draft,
    finalize_post,
)

def build_hitl_graph():

    """
    Workflow:

        START
          → analyze_content
          → research_online
          → generate_draft
          → review_draft
          → decide_next_step
              - if approve → finalize_post → END
              - if revise  → revise_draft → review_draft (loop)
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("analyze_content", analyze_content)
    graph.add_node("generate_draft", generate_draft)
    # graph.add_node("research_online", research_online)
    
    graph.add_node("review_draft", review_draft)
    graph.add_node("decide_next_step", decide_next_step)
    graph.add_node("revise_draft", revise_draft)
    graph.add_node("finalize_post", finalize_post)

    graph.add_edge(START, "analyze_content")
    graph.add_edge("analyze_content", "generate_draft")
    # graph.add_edge("analyze_content", "research_online")
    # graph.add_edge("research_online", "generate_draft")
    graph.add_edge("generate_draft", "review_draft")

    graph.add_edge("decide_next_step", "revise_draft")
    graph.add_edge("decide_next_step", "finalize_post")

    # loop back to review after revision
    graph.add_edge("revise_draft", "review_draft")

    graph.add_edge("finalize_post", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)