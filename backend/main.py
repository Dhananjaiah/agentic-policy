from fastapi import FastAPI
from pydantic import BaseModel

from .graph_app import run_insurance_agent

app = FastAPI(title="Agentic Insurance Assistant")


class ChatRequest(BaseModel):
    userId: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    data: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = run_insurance_agent(req.userId, req.message)
    return ChatResponse(answer=result["answer"], data=result.get("raw"))

