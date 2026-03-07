# main.py
from graph.builder import build_basic_graph
from graph.state import WorkflowState


def run_basic_workflow():
    print("=== LinkedIn Post Draft Workflow (Basic) ===")
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

    app = build_basic_graph()

    initial_state = WorkflowState(raw_input=raw_text)

    final_state = app.invoke(initial_state)

    print("\n\n=== ANALYSIS ===\n")
    print(final_state.analysis or "(no analysis)")

    print("\n\n=== DRAFT POST (v{v}) ===\n".format(v=final_state.version))
    print(final_state.draft_post or "(no draft)")


if __name__ == "__main__":
    run_basic_workflow()
