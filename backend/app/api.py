from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from app.models import Chat, SynapseGenerationResponse
from app.llm import generate_synapse

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/generate-synapse", response_model=SynapseGenerationResponse)
async def stream_data(chat: Chat, response: Response):
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    
    return StreamingResponse(generate_synapse(chat))
