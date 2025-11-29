from typing import Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from .tools_langchain import get_policy, get_claim, get_documents

# Load OPENAI_API_KEY etc.
load_dotenv(".env.local")

# 1) LLM model (real model, not fake logic)
model = ChatOpenAI(
    model="gpt-4o-mini",  # change if you want
    temperature=0.1,
)

# 2) Tools – plain Python funcs, agent will call them as tools
tools = [get_policy, get_claim, get_documents]

# 3) Agent – this is LangChain's agent built on LangGraph v1
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=(
        "You are an insurance assistant. "
        "User will ask about policy IDs and claim IDs. "
        "Use the tools to fetch real data from the database. "
        "Always answer in short, simple sentences. "
        "If something is not found, say that clearly."
    ),
)


def run_insurance_agent(user_id: str, message: str) -> Dict[str, Any]:
    """
    Run the insurance agent for a single user message.

    We pass messages -> agent decides tools -> returns full message list.
    """
    state = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": message}
            ]
        }
    )

    # state is a dict with "messages" (AgentState) 
    messages = state.get("messages", [])
    final_msg = messages[-1] if messages else None
    answer_text = getattr(final_msg, "content", "") if final_msg is not None else ""

    # Make messages JSON-friendly for debug in API
    debug_messages = []
    for m in messages:
        debug_messages.append(
            {
                "type": getattr(m, "type", None),
                "content": getattr(m, "content", None),
            }
        )

    return {
        "answer": answer_text,
        "raw": {
            "messages": debug_messages,
        },
    }

