# graph/nodes.py
from langgraph.types import Command, interrupt
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import DEFAULT_AUDIENCE,DEFAULT_POST_GOAL,DEFAULT_TONE
from llm.provider import get_llm
from graph.state import WorkflowState
from tools.web_research import run_web_search


def ingest_input(state: WorkflowState) -> WorkflowState:
    """
    Node: starting point. For now, this will just assume `raw_input`
    is already set in the state (we'll set it from CLI later).
    """
    # Later we might add initial normalization here.
    return state


def analyze_content(state: WorkflowState) -> WorkflowState:
    """
    Use the LLM to understand the raw input, extract key points, and
    identify gaps or missing context that might need research.
    """
    if not state.raw_input:
        # nothing to do here
        return state 
    

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert content strategist helping to prepare LinkedIn posts. "
            "You analyze the user's raw notes and produce a structured analysis.",
        ),
        (
            "human",
            "Here is the raw content:\n\n"
            "{text}\n\n"
            "Please respond with a clear structured analysis with the following sections:\n"
            "1) Summary (2–3 sentences)\n"
            "2) Key Points (bullet list)\n"
            "3) Gaps or Missing Context (bullet list, focusing on facts, data, or clarity that might be needed)\n",
        ),
    ])

    chain = prompt | llm | StrOutputParser()

    analysis_text = chain.invoke({'text': state.raw_input})

    state.analysis = analysis_text
    return state


def research_online(state: WorkflowState) -> WorkflowState:
    """
    Real research node:
      1) Ask LLM to propose 2-3 concrete web search queries.
      2) Call Tavily with those queries.
      3) Summarize findings into research_notes and keep raw results.
    """
    if not state.analysis:
        return state

    llm = get_llm()

    # Step 1: generate search queries from analysis
    query_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You suggest focused web search queries for fact-checking and enrichment "
            "of a LinkedIn post idea.",
        ),
        (
            "human",
            "Here is the structured analysis of a LinkedIn post:\n\n"
            "{analysis}\n\n"
            "Based on this, propose 2-4 concise web search queries that would help "
            "find:\n"
            "- statistics or data points\n"
            "- concrete examples or case studies\n"
            "- definitions or explanations of key concepts\n\n"
            "Return them as a bullet list, one query per line.",
        ),
    ])

    query_chain = query_prompt | llm | StrOutputParser()
    queries_text = query_chain.invoke({"analysis": state.analysis})

    # Extract lines starting with '-' or '*'
    raw_lines = [line.strip("-• ").strip() for line in queries_text.splitlines() if line.strip()]
    search_queries = [q for q in raw_lines if q]

    if not search_queries:
        state.research_notes = "No specific web research queries generated."
        return state

    # Step 2: call Tavily
    search_results = run_web_search(search_queries)

    # Step 3: summarize findings back into research_notes
    summary_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You summarize web research into concise notes for a LinkedIn post. "
            "Focus on: key facts, useful examples, and how they support the main idea.",
        ),
        (
            "human",
            "Original analysis:\n\n{analysis}\n\n"
            "Search queries used:\n{queries}\n\n"
            "Raw search results (title, url, content):\n{results}\n\n"
            "Produce 'Research Notes' with:\n"
            "1) Key facts and data points (bullet list, mention source name).\n"
            "2) Examples or case studies worth referencing.\n"
            "3) Any cautions or uncertainties in the data.\n",
        ),
    ])

    summary_chain = summary_prompt | llm | StrOutputParser()
    results_str = "\n\n".join(
        f"- [{r['query']}] {r['title']} ({r['url']})\n{r['content']}"
        for r in search_results
    )

    research_notes = summary_chain.invoke(
        {
            "analysis": state.analysis,
            "queries": "\n".join(f"- {q}" for q in search_queries),
            "results": results_str[:8000],  # safety: truncate long content
        }
    )

    state.research_notes = research_notes
    # Optional: keep raw results on state if you add a field for it
    # state.research_results = search_results
    return state


def generate_draft(state: WorkflowState) -> WorkflowState:
    """
    Generate a LinkedIn-style post using the analysis (and optionally research notes).
    The post should have:
      - A strong hook (1–2 lines)
      - A clear, readable body
      - A closing line / CTA
    """

    if not state.analysis:
        #nothing to do
        return state
    

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior LinkedIn content writer. "
            "You turn structured analysis into engaging LinkedIn posts.\n"
            f"Target audience: {DEFAULT_AUDIENCE}.\n"
            f"Tone: {DEFAULT_TONE}.\n"
            f"Goal: {DEFAULT_POST_GOAL}.\n"
            "Write in a way that is scannable, conversational, and clear.",
        ),
        (
            "human",
            "Here is the structured analysis of the user's idea:\n\n"
            "{analysis}\n\n"
            "If available, here are some additional research notes:\n\n"
            "{research_notes}\n\n"
            "Now write a LinkedIn post with the following structure:\n"
            "- Start with a strong hook (1–2 short lines) that grabs attention.\n"
            "- Then explain the main idea in a relatable, story-like way using short paragraphs.\n"
            "- Use line breaks for readability; avoid long walls of text.\n"
            "- End with a simple call to action (e.g., ask a question or invite opinions).\n"
            "Do NOT include hashtags for now. Do NOT add emojis unless it really fits.\n",
        ),
    ])

    chain = prompt | llm | StrOutputParser()

    research_notes = state.research_notes or "No extra research notes yet."
    draft = chain.invoke(
        {
            "analysis": state.analysis,
            "research_notes": research_notes
        }
    )

    state.draft_post = draft
    state.version += 1
    return state


def safety_tone_check(state: WorkflowState) -> WorkflowState:
    """
    Node: ensure the post is safe and matches desired tone.
    """
    llm = get_llm()
    # TODO: implement later
    return state


def apply_suggestions(state: WorkflowState) -> WorkflowState:
    """
    Node: revise the draft based on human feedback.
    """
    llm = get_llm()
    # TODO: implement later
    return state


def review_draft(state: WorkflowState) -> dict:
    """
    Pause and ask human to review the current draft.
    interrupt() will:
      - First run: pause and surface payload under __interrupt__.
      - Resume: return the value passed in Command(resume=...).
    """
    if not state.draft_post:
        # Nothing to review, just move on — no interrupt.
        return {"final_post": state.draft_post}

    # Ask for review
    payload = interrupt({
        "draft": state.draft_post,
        "version": state.version,
        "instructions": (
            "Options:\n"
            "1) Type 'approve' to accept as-is.\n"
            "2) Type 'revise' and give comments about what to change.\n"
            "3) Type 'edit' and paste your fully edited version.\n"
        ),
    })

    # On first run, we never get here (graph pauses).
    # On resume, payload is whatever we passed in Command(resume=...).
    decision = (payload or {}).get("decision", "approve")
    comment = (payload or {}).get("comment")
    edited_text = (payload or {}).get("edited_text")

    if decision == "edit" and edited_text:
        return {
            "review_decision": "edit",
            "review_comment": comment,
            "final_post": edited_text,
        }
    else:
        return {
            "review_decision": decision,
            "review_comment": comment,
        }
    
def decide_next_step(state: WorkflowState) -> str:
    """
    Decide whether to finalize or revise based on human review.
    """
    if state.review_decision == "revise":
        return "revise_draft"
    # approve OR edit both go to finalize_post
    return "finalize_post"

def revise_draft(state: WorkflowState) -> WorkflowState:
    """
    Use the LLM to revise the draft based on human comments/edits.
    """
    if not state.draft_post:
        return state

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior LinkedIn content editor. "
            "You revise the draft based on the human review comments.",
        ),
        (
            "human",
            "Here is the current draft (version {version}):\n\n"
            "{draft}\n\n"
            "Here is the human feedback/comment:\n\n"
            "{comment}\n\n"
            "Please produce an improved LinkedIn post that respects the feedback. "
            "Keep it concise, readable, and in the same general style.",
        ),
    ])

    chain = prompt | llm | StrOutputParser()

    feedback = state.review_comment or "No specific comments, just improve it."

    new_draft = chain.invoke(
        {
            "draft": state.draft_post,
            "version": state.version,
            "comment": feedback,
        }
    )

    state.draft_post = new_draft
    state.version += 1
    # Clear previous decision so we can review again
    state.review_decision = None
    state.review_comment = None
    return state


def finalize_post(state: WorkflowState) -> WorkflowState:
    """
    Finalize: if human already provided edited text, keep it.
    Otherwise, copy the last draft into final_post.
    """
    if not state.final_post:
        state.final_post = state.draft_post
    return state