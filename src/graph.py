from schemas import GraphState
import stt
import llm
import logging
from uuid import uuid4
from langgraph.graph import END, StateGraph


logger = logging.getLogger(__name__)


def transcribe_node(state: GraphState) -> dict:
    return {"raw_transcript": stt.transcribe_file(state.audio_path)}


def log_transcript_node(state: GraphState) -> dict:
    """Zrzuca surową transkrypcję do logów — bez korekty, bez wywołania LLM."""
    logger.info(
        "transkrypcja audio_path=%s raw_transcript=%r",
        state.audio_path,
        state.raw_transcript,
    )
    return {}


def classify_intent_node(state: GraphState) -> dict:
    return {"intent": llm.classify_intent(state.raw_transcript)}

def _consultant_handoff(reason: str) -> dict:
    ticket_id = uuid4().hex[:8]
    return {
        "answer": f"Przekazuję rozmowę do konsultanta (zgłoszenie #{ticket_id}). Powód: {reason}",
        "escalated": True,
    }

def faq_answer_node(state: GraphState) -> dict:
    result = llm.answer_faq(state.intent.category, state.intent.question)
    if not result.found:
        return _consultant_handoff(state.intent.question)
    return {"answer": result.answer, "escalated": False}


def log_faq_answer_node(state: GraphState) -> dict:
    logger.info(
        "odpowiedz_faq category=%s escalated=%s answer=%r",
        state.intent.category,
        state.escalated,
        state.answer,
    )
    return {}


def route_after_classify(state: GraphState) -> str:
    return "consultant" if state.intent.category == "consultant" else "faq"


def route_to_consultant_node(state: GraphState) -> dict:
    return _consultant_handoff(state.intent.question)



def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("transcribe", transcribe_node)
    graph.add_node("log_transcript", log_transcript_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("faq_answer", faq_answer_node)
    graph.add_node("log_faq_answer", log_faq_answer_node)
    graph.add_node("route_to_consultant", route_to_consultant_node)

    graph.set_entry_point("transcribe")
    graph.add_edge("transcribe", "log_transcript")
    graph.add_edge("log_transcript", "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {"faq": "faq_answer", "consultant": "route_to_consultant"},
    )
    graph.add_edge("faq_answer", "log_faq_answer")
    graph.add_edge("log_faq_answer", END)
    graph.add_edge("route_to_consultant", END)
    return graph.compile()
