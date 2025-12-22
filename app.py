import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from llm_client import ask_llm
from extractor import extract_and_validate
from prompts import PROMPT_MAP, SYSTEM_DEFAULT_MODE

app = FastAPI(title="Bilmo LLM API", version="1.0.0")

# Configure CORS - allow specific origins in production via ALLOWED_ORIGINS env var
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bilmo LLM API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    mode: Optional[str] = "default"  # Mode: "default", "health", or "budget"

@app.post("/chat")
async def chat(req: ChatRequest):
    # Get the appropriate prompt based on mode
    mode = req.mode.lower() if req.mode else "default"
    system_prompt = PROMPT_MAP.get(mode, SYSTEM_DEFAULT_MODE)
    
    messages = [{"role": "system", "content": system_prompt}] + \
               [m.dict() for m in req.messages]

    reply = ask_llm(messages)
    return {"assistant": reply}

@app.post("/finalize")
async def finalize(req: ChatRequest):
    # Get the appropriate prompt based on mode
    mode = req.mode.lower() if req.mode else "default"
    system_prompt = PROMPT_MAP.get(mode, SYSTEM_DEFAULT_MODE)
    
    messages = [{"role": "system", "content": system_prompt}] + \
               [m.dict() for m in req.messages] + [
                   {"role": "system", "content": "Now return ONLY the final JSON."}
               ]

    reply = ask_llm(messages)
    ok, data = extract_and_validate(reply)

    return {
        "success": ok,
        "data": data
    }
