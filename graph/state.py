# graph/state.py
from typing import List, Literal, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


ReviewStatus = Literal["pending", "approved", "changes_requested"]


class WorkflowState(BaseModel):
    """
    Core state that flows through the LangGraph workflow.

    This is intentionally explicit so it's easy to inspect and debug.
    """

    # Conversation-style messages (optional, useful for debugging / UI)
    messages: List[BaseMessage] = Field(default_factory=list)

    # Input & understanding
    raw_input: Optional[str] = None            # Raw paragraphs from user
    analysis: Optional[str] = None             # LLM's understanding / key points / gaps

    # Research & enrichment
    research_notes: Optional[str] = None       # Notes from web research / fact-check

    # Draft generation & evolution
    draft_post: Optional[str] = None           # Current LinkedIn draft
    version: int = 0                           # Draft version counter

    # Human-in-the-loop review
    review_status: ReviewStatus = "pending"    # pending | approved | changes_requested
    human_feedback: Optional[str] = None       # Suggestions from human reviewer

    # Publishing result
    publish_result: Optional[str] = None       # e.g., LinkedIn URL / ID / mock path
