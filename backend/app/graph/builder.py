"""
LangGraph graph builder.

Compiles and exports the complete video_generation_graph.
This is the ONLY place where the graph topology is defined.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.checkpointer import FirebaseCheckpointer
from app.graph.edges import (
    route_after_content_generation,
    route_after_execution,
    route_after_manim_script,
    route_after_narration,
    route_after_ocr,
    route_after_repair,
    route_after_supervisor,
    route_after_synchronization,
)
from app.graph.nodes import (
    content_generation_node,
    error_handler_node,
    finalize_node,
    manim_execution_node,
    manim_script_node,
    narration_agent_node,
    ocr_agent_node,
    repair_agent_node,
    supervisor_node,
    synchronization_node,
)
from app.schemas.state import VideoGenerationState


def build_video_generation_graph() -> StateGraph:
    """
    Build and return the compiled LangGraph StateGraph.

    Graph topology:
        START
          └─> supervisor
                ├─(requires_ocr)─> ocr_agent
                │                     └─> content_generation_agent
                └─(plain text)──────> content_generation_agent
                                          └─> manim_script_agent
                                                └─> manim_execution_service
                                                      ├─(success)─> narration_agent
                                                      │               └─> synchronization_service
                                                      │                       └─> finalize ──> END
                                                      └─(failure)─> repair_agent
                                                                      └─> manim_execution_service
                                                                            (loop until success or max retries)
        Any node failure ──> error_handler ──> END
    """
    workflow = StateGraph(VideoGenerationState)

    # ── Add nodes ──────────────────────────────────────────────────────────
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("ocr_agent", ocr_agent_node)
    workflow.add_node("content_generation_agent", content_generation_node)
    workflow.add_node("manim_script_agent", manim_script_node)
    workflow.add_node("manim_execution_service", manim_execution_node)
    workflow.add_node("repair_agent", repair_agent_node)
    workflow.add_node("narration_agent", narration_agent_node)
    workflow.add_node("synchronization_service", synchronization_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_node("error_handler", error_handler_node)

    # ── Entry point ────────────────────────────────────────────────────────
    workflow.add_edge(START, "supervisor")

    # ── Conditional edges ──────────────────────────────────────────────────
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "ocr_agent": "ocr_agent",
            "content_generation_agent": "content_generation_agent",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "ocr_agent",
        route_after_ocr,
        {
            "content_generation_agent": "content_generation_agent",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "content_generation_agent",
        route_after_content_generation,
        {
            "manim_script_agent": "manim_script_agent",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "manim_script_agent",
        route_after_manim_script,
        {
            "manim_execution_service": "manim_execution_service",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "manim_execution_service",
        route_after_execution,
        {
            "narration_agent": "narration_agent",
            "repair_agent": "repair_agent",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "repair_agent",
        route_after_repair,
        {
            "manim_execution_service": "manim_execution_service",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "narration_agent",
        route_after_narration,
        {
            "synchronization_service": "synchronization_service",
            "error_handler": "error_handler",
        },
    )

    workflow.add_conditional_edges(
        "synchronization_service",
        route_after_synchronization,
        {
            "finalize": "finalize",
            "error_handler": "error_handler",
        },
    )

    # ── Terminal edges ─────────────────────────────────────────────────────
    workflow.add_edge("finalize", END)
    workflow.add_edge("error_handler", END)

    return workflow


from langgraph.checkpoint.memory import MemorySaver

# Use MemorySaver to bypass Firestore for local development
_checkpointer = MemorySaver()

def get_compiled_graph(checkpointer=None):
    """Return the compiled LangGraph app with Memory checkpointing."""
    workflow = build_video_generation_graph()
    # Compile graph
    cp = checkpointer if checkpointer is not None else _checkpointer
    return workflow.compile(checkpointer=cp)


# Eager singleton (initialized on first import after Firebase is ready)
_compiled_graph = None


def get_graph():
    """
    Lazy singleton accessor for the compiled graph.
    Call this after Firebase has been initialized.
    """
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = get_compiled_graph()
    return _compiled_graph
