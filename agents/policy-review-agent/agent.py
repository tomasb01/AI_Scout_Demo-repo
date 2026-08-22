"""Policy review agent.

Autonomously walks the policy-document inbox, extracts key terms,
cross-checks them against the contract database and files correction
tickets — replans on failure until the inbox is empty.
"""

import operator
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode


@tool
def read_policy_document(path: str) -> str:
    """Read a policy document from the inbox directory."""
    with open(path) as f:
        return f.read()


@tool
def query_contract_db(policy_number: str) -> str:
    """Fetch the stored contract terms for a policy number."""
    import sqlite3

    conn = sqlite3.connect("contracts.db")
    row = conn.execute(
        "SELECT terms_json FROM contracts WHERE policy_number = ?",
        (policy_number,),
    ).fetchone()
    conn.close()
    return row[0] if row else "NOT_FOUND"


@tool
def file_correction_ticket(policy_number: str, discrepancy: str) -> str:
    """File a correction ticket for a mismatched policy."""
    with open("tickets.log", "a") as f:
        f.write(f"{policy_number}: {discrepancy}\n")
    return "ticket filed"


TOOLS = [read_policy_document, query_contract_db, file_correction_ticket]

llm = ChatAnthropic(model="claude-sonnet-5").bind_tools(TOOLS)

MAX_ITERATIONS = 25


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    iterations: int


def agent_node(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response], "iterations": state["iterations"] + 1}


def should_continue(state: AgentState) -> str:
    # Autonomous loop: keeps replanning until done or iteration cap hit.
    if state["iterations"] >= MAX_ITERATIONS:
        return END
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END


graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app = graph.compile()


if __name__ == "__main__":
    result = app.invoke(
        {
            "messages": [
                (
                    "user",
                    "Process every document in ./inbox: extract policy number "
                    "and terms, compare against the contract DB, and file a "
                    "ticket for every discrepancy. Keep going until the inbox "
                    "is fully processed.",
                )
            ],
            "iterations": 0,
        }
    )
    print(f"Done after {result['iterations']} iterations.")
