# graph/nodes.py
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import DEFAULT_AUDIENCE,DEFAULT_POST_GOAL,DEFAULT_TONE
from llm.provider import get_llm
from graph.state import WorkflowState


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
    Node: call web research tools to fact-check and enrich.
    """
    # TODO: implement later when we add web tools
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

if __name__ == "__main__":
    # Quick manual test
    sample_input = """
    I want to talk about how learning LangChain and LangGraph changed
    the way I think about building AI apps. I used to just call an API,
    now I can design proper workflows, RAG, and agents.
    """

    state = WorkflowState(raw_input=sample_input)

    state = analyze_content(state)
    print("\n=== ANALYSIS ===\n")
    print(state.analysis)

    state = generate_draft(state)
    print("\n=== DRAFT POST (v{v}) ===\n".format(v=state.version))
    print(state.draft_post)