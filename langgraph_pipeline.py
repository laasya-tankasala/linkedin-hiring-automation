from typing import TypedDict
from langgraph.graph import StateGraph, START, END
import requests
from linkedIn_api_mocks import search_candidates, send_message

# -- Replace with your actual OpenAI API config
LLM_API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "sk-..."  # Replace with your key

# Define shared state type
class PipelineState(TypedDict):
    keywords: list[str]
    role: str
    candidates: list[dict]
    messages: list[dict]

# Helper function to call LLM
def call_llm(prompt, context):
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a hiring assistant."},
            {"role": "user", "content": prompt}
        ],
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.post(LLM_API_URL, json=payload, headers=headers)
    return resp.json()["choices"][0]["message"]["content"]

# --- Pipeline node functions ---

def find_candidates(state: PipelineState) -> PipelineState:
    state["candidates"] = search_candidates(state["keywords"])
    return state

def generate_messages(state: PipelineState) -> PipelineState:
    messages = []
    for c in state["candidates"]:
        prompt = f"Create outreach for {c['name']} for role {state['role']}"
        ctx_resp = requests.get(f"http://localhost:8000/mcp/context/{c['id']}").json()
        text = call_llm(prompt, ctx_resp.get("context", {}))
        messages.append({"cand": c, "msg": text})
    state["messages"] = messages
    return state

def update_context(state: PipelineState) -> PipelineState:
    for m in state["messages"]:
        requests.post("http://localhost:8000/mcp/context", json={
            "session_id": m["cand"]["id"],
            "user": "recruiter",
            "context": {"last": m["msg"]}
        })
    return state

def send_outreach(state: PipelineState) -> PipelineState:
    for m in state["messages"]:
        send_message(m["cand"]["id"], m["msg"])
    return state

# --- LangGraph pipeline wiring ---
def run_pipeline():
    builder = StateGraph(PipelineState)

    builder.add_node("find_candidates", find_candidates)
    builder.add_node("generate_messages", generate_messages)
    builder.add_node("update_context", update_context)
    builder.add_node("send_outreach", send_outreach)

    builder.add_edge(START, "find_candidates")
    builder.add_edge("find_candidates", "generate_messages")
    builder.add_edge("generate_messages", "update_context")
    builder.add_edge("update_context", "send_outreach")
    builder.add_edge("send_outreach", END)

    app = builder.compile()
    output = app.invoke({
        "keywords": ["Python", "Django"],
        "role": "Software Engineer"
    })

    print("Pipeline finished!")
    return output

if __name__ == "__main__":
    run_pipeline()
