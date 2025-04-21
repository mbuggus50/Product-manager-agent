#requirement_agent/schema.py
from typing import List, Optional
from pydantic import BaseModel, Field

REQUIRED_FIELDS = ["business_need", "business_impact"]

class PRD(BaseModel):
    raw_request: str
    business_need: Optional[str] = None
    business_impact: Optional[str] = None

class IntakeState(BaseModel):
    user_id: str
    messages: List[str] = Field(default_factory=list)
    prd: PRD
    missing: List[str] = Field(default_factory=list)
    done: bool = False


#requirement_agent/nodes.py
from typing import List
from datetime import datetime
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from .schema import IntakeState, REQUIRED_FIELDS

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)  # swap / stub as desired

def _find_missing(prd_dict) -> List[str]:
    return [f for f in REQUIRED_FIELDS if not prd_dict.get(f)]

# ────────────────────────────────────────────────────────────────
def intake(state: IntakeState) -> IntakeState:
    state.messages.append(f"[{datetime.utcnow()}] Intake received")
    return state

def validate(state: IntakeState):
    missing = _find_missing(state.prd.model_dump())
    if missing:
        state.missing = missing
        prompt = (
            f"I still need {', '.join(missing)}.\n"
            "Please answer in JSON, e.g. "
            + ", ".join([f"\"{f}\": \"…\"" for f in missing])
        )
        state.messages.append(prompt)
        return interrupt(state)  # ← pause & hand payload to caller
    state.missing = []
    return state

def clarify(state: IntakeState):
    # Normally you'd craft a richer question w/ RAG. Here we echo the prompt.
    question = state.messages[-1]
    _ = llm.invoke(question)  # could enrich, log token usage, etc.
    return state

def merge(state: IntakeState):
    state.messages.append("Patch merged ✅")
    return state

def generate_prd(state: IntakeState):
    md = (
        f"# Product Requirement Document\n\n"
        f"**Business Need**  \n{state.prd.business_need}\n\n"
        f"**Business Impact**  \n{state.prd.business_impact}\n"
    )
    state.messages.append("PRD generated ✅")
    state.done = True
    state.prd_markdown = md  # store for UI / S3 later
    return state
# ────────────────────────────────────────────────────────────────
#requirement_agent/builder.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .schema import IntakeState
from .nodes import intake, validate, clarify, merge, generate_prd

def build_graph(checkpointer=None):
    cp = checkpointer or MemorySaver()

    builder = StateGraph(IntakeState)

    builder.add_node("Intake", intake)
    builder.add_node("Validate", validate)
    builder.add_node("Clarify", clarify)
    builder.add_node("Merge", merge)
    builder.add_node("GeneratePRD", generate_prd)

    builder.set_entry_point("Intake")

    # branching logic: one successor only
    builder.add_conditional_edges(
        "Validate",
        lambda s: "Clarify" if s.missing else "GeneratePRD"
    )
    builder.add_edge("Clarify", "Merge")
    builder.add_edge("Merge", "Validate")
    builder.add_edge("GeneratePRD", END)

    return builder.compile(checkpointer=cp)
# ────────────────────────────────────────────────────────────────
#demo.py – a tiny “UI”
import json, sys
from uuid import uuid4
from rich import print as rprint
from requirement_agent.builder import build_graph
from requirement_agent.schema import IntakeState, PRD

graph = build_graph()                       # global compiled graph


# ────────────────────────────────────────────────────────────────────
def _state_from_events(events, thread_id: str) -> IntakeState:
    """
    Extract the last state snapshot from an event stream.
    Falls back to graph.get_state() if none found.
    """
    last = None
    for ev in events:
        if ev.get("event") in ("on_node_end", "on_interruption"):
            last = ev["value"]              # AddableUpdatesDict -> dict

    if last is None:                       # rare, but be defensive
        last = graph.get_state(
            {"configurable": {"thread_id": thread_id}}
        ).values

    return IntakeState.model_validate(last)


def run_session(initial_request: str, scripted_patches: list[dict] | None = None):
    """Interactive or head‑less clarification loop."""
    tid = str(uuid4())

    # 1️⃣ kick‑off ------------------------------------------------------------
    start_state = IntakeState(
        user_id="demo-user",
        prd=PRD(raw_request=initial_request),
        messages=[initial_request],
    )

    state = _state_from_events(
        graph.stream(
            start_state,
            config={"configurable": {"thread_id": tid}},
            stream_mode="events",           # *** IMPORTANT FIX ***
        ),
        tid,
    )
    show(state)

    # 2️⃣ resume until PRD ready ---------------------------------------------
    patches = list(scripted_patches or [])
    while not state.done:
        patch = (
            patches.pop(0)
            if patches
            else json.loads(input("[bold yellow]Enter JSON patch → [/] "))
        )
        if scripted_patches:
            rprint(f"[cyan]auto‑patch:[/] {patch}")

        # 👉 1. wrap under 'prd'
        update = {"prd": patch}

        # 👉 2. send as Command(resume=…)
        cmd = Command(resume=update)

        state = _state_from_events(
            graph.stream(
                cmd,
                config={"configurable": {"thread_id": tid}},
                stream_mode="events",
            ),
            tid,
        )
        show(state)


# ────────────────────────────────────────────────────────────────────
def show(s: IntakeState):
    rprint("\n[bold]Messages so far:[/]")
    for m in s.messages:
        rprint(f"• {m}")
    if s.missing:
        rprint(f"[red]Still missing:[/] {s.missing}")
    if s.done:
        rprint("\n[green]=== FINAL PRD ===[/]\n")
        rprint(s.prd_markdown)
        rprint("[green]==================[/]\n")


# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        run_session(
            "Need a button that increases engagement.",
            [
                {"business_need": "Add a prominent CTA button on homepage"},
                {"business_impact": "Increase CTR by 15% and conversions by 5%"},
            ],
        )
    else:
        run_session("Need a button that increases engagement.")
