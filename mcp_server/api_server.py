from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class ContextPayload(BaseModel):
    session_id: str
    user: str
    context: dict

# In-memory context store
context_store = {}

@app.post("/mcp/context")
async def update_context(payload: ContextPayload):
    context_store[payload.session_id] = payload.context
    return {"status": "ok"}

@app.get("/mcp/context/{session_id}")
async def get_context(session_id: str):
    ctx = context_store.get(session_id, {})
    return {"session_id": session_id, "context": ctx}
