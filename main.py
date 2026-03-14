# main.py
from graph.builder import build_hitl_graph
from graph.state import WorkflowState
from langgraph.types import Command


def run_hitl_workflow():
    print("=== LinkedIn Post Draft Workflow (Human-in-the-Loop) ===")
    print("Paste your raw idea/content below. End with an empty line.\n")

    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    raw_text = "\n".join(lines).strip()

    if not raw_text:
        print("No input provided. Exiting.")
        return

    app = build_hitl_graph()

    # Use a thread_id so we can resume the same run
    config = {"configurable": {"thread_id": "cli-thread-1"}}

    # Run until first interrupt or end
    print("\nRunning graph...\n")
    state: WorkflowState | None = None

    # First run: will either finish or hit interrupt
    result = app.invoke(WorkflowState(raw_input=raw_text).model_dump(), config=config)

    # result is a dict, possibly with "__interrupt__"
    interrupts = result.get("__interrupt__")
    
    if interrupts:
        # Our review_draft node passed a review_request dict to interrupt()
        review_request = interrupts[0].value  # {"draft": ..., "version": ..., "instructions": ...}

        print("\n=== DRAFT FOR REVIEW (v{v}) ===\n".format(v=review_request["version"]))
        print(review_request["draft"])
        print("\n" + review_request["instructions"])

        mode = input("\nChoose: 'a' = approve, 'r' = revise with comments, 'e' = paste edited draft: ").strip().lower()
        if mode == "a":
            payload = {"decision": "approve"}
        elif mode == "r":
            comment = input("Enter your comments/edits: ").strip()
            payload = {"decision": "revise", "comment": comment}
        else:
            print("\nPaste your edited version below. End with an empty line.\n")
            lines = []
            while True:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            edited = "\n".join(lines).strip()
            payload = {"decision": "edit", "edited_text": edited}

        # Resume the graph with the decision
        final_state_dict = app.invoke(Command(resume=payload), config=config)
        final_state = WorkflowState(**{k: v for k, v in final_state_dict.items() if k != "__interrupt__"})
        # final_state = WorkflowState(**final_state_dict)

        print("\n=== FINAL POST (v{v}) ===\n".format(v=final_state.version))
        print(final_state.final_post or final_state.draft_post)
    else:
        # No interrupt: graph reached END in one shot
        final_state = WorkflowState(**{k: v for k, v in result.items() if k != "__interrupt__"})
        print("\n=== FINAL POST (v{v}) ===\n".format(v=final_state.version))
        print(final_state.final_post or final_state.draft_post)


if __name__ == "__main__":
    run_hitl_workflow()
