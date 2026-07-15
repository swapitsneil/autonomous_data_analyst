from langgraph.graph import StateGraph, END

from models.state import WorkflowState

from agents.profiler import profile_dataset
from agents.hypothesis import generate_hypotheses
from agents.analyst import analyze_hypotheses
from agents.critic import review_analysis
from agents.narrator import generate_report

from memory.memory_agent import memory_agent


# Profiler Agent

def profiler_node(state):

    state["profile"] = profile_dataset(
        state["df"]
    )

    return state


# Hypothesis Agent

def hypothesis_node(state):

    state["hypotheses"] = generate_hypotheses(
        state["profile"]
    )

    return state


# Analyst Agent

def analyst_node(state):

    state["analysis"] = analyze_hypotheses(
        state["df"],
        state["hypotheses"]
    )

    return state


# Critic Agent

def critic_node(state):

    state["critic"] = review_analysis(
        state["hypotheses"],
        state["analysis"]
    )

    return state


# Retry Incrementer Node

def retry_incrementer_node(state):

    state["retry_count"] += 1

    print(
        f"\nRetrying Analysis Workflow "
        f"({state['retry_count']}/3)..."
    )

    return state


# Narrator Agent

def narrator_node(state):

    if state["critic"].get("status") != "success":

        state["report"] = {
            "agent": "Narrator Agent",
            "status": "skipped",
            "reason": "Critic Agent failed."
        }

        return state

    try:

        approved_ids = {

            review["id"]

            for review in state["critic"].get("reviews", [])
            if review.get("approved")

        }

        approved_hypotheses = {

            "hypotheses": [

                hypothesis

                for hypothesis in state["hypotheses"].get(
                    "hypotheses",
                    []
                )

                if hypothesis["id"] in approved_ids

            ]

        }

        approved_analysis = {

            "analysis": [
                analysis
                for analysis in state["analysis"].get("analysis", [])
                if analysis["id"] in approved_ids
            ]

        }

        state["report"] = generate_report(
            approved_hypotheses,
            approved_analysis,
            state["critic"]
        )

    except Exception as e:

        print(f"\nNarrator Agent Failed: {e}")

        state["report"] = {
            "agent": "Narrator Agent",
            "status": "failed",
            "error": str(e)
        }

    return state


# Memory Agent

def memory_node(state):

    if state["report"].get("status") != "success":

        print("\nSkipping Memory Agent.")

        state["memory"] = {
            "agent": "Memory Agent",
            "status": "skipped",
            "reason": "Narrator Agent did not complete successfully."
        }

        return state

    try:

        state["memory"] = memory_agent(
            state["df"],
            state["profile"],
            state["report"]
        )

    except Exception as e:

        state["memory"] = {
            "agent": "Memory Agent",
            "status": "failed",
            "error": str(e)
        }

    return state


# Retry Router

def should_retry(state):

    critic = state["critic"]

    # Quota exhausted or hard failure — skip retries
    if critic.get("status") == "failed":
        error_msg = str(critic.get("error", "")).upper()
        if any(k in error_msg for k in ["429", "QUOTA", "RESOURCE_EXHAUSTED", "LIMIT"]):
            print("\n[WARNING] Gemini quota exhausted. Skipping retries.")
            return "narrator"

    if critic.get("status") != "success":
        return "narrator"

    rejected = [
        review
        for review in critic.get("reviews", [])
        if not review.get("approved")
    ]

    if len(rejected) == 0:
        return "narrator"

    if state["retry_count"] >= 3:
        return "narrator"

    return "retry_incrementer"


workflow = StateGraph(WorkflowState)
workflow.add_node("profiler", profiler_node)
workflow.add_node("hypothesis", hypothesis_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("critic", critic_node)
workflow.add_node("retry_incrementer", retry_incrementer_node)
workflow.add_node("narrator", narrator_node)
workflow.add_node("memory", memory_node)

workflow.set_entry_point("profiler")
workflow.add_edge("profiler", "hypothesis")
workflow.add_edge("hypothesis", "analyst")
workflow.add_edge("analyst", "critic")

workflow.add_conditional_edges(
    "critic",
    should_retry,
    {
        "retry_incrementer": "retry_incrementer",
        "narrator": "narrator"
    }
)

workflow.add_edge("retry_incrementer", "hypothesis")
workflow.add_edge("narrator", "memory")
workflow.add_edge("memory", END)

graph = workflow.compile()