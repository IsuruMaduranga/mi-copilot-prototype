from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from models.base import ChatRequest, ChatResponse
from ai.copilot import Copilot

api = FastAPI()
copilot = Copilot()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/code-gen-chat", response_model=ChatResponse)
async def code_gen_chat(request: ChatRequest, response: Response):
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    
    return StreamingResponse(copilot.code_gen_chat(request.messages))
