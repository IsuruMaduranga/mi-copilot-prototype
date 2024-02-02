from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
from models import Chat, Message
import toml

load_dotenv()

client = OpenAI()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read system.prompt file
with open("system.prompt", "r") as f:
    system_msg_txt = f.read()
    
with open("config.toml", "r") as f:
    config = toml.load(f)
    print(config)
    
system_msg = Message(role="system", content=system_msg_txt)

def generate_synapse(chat: Chat):        
    stream = client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=list(chat.chat_history),
        stream=True,
    )   
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield f"{chunk.choices[0].delta.content}\n\n"

@app.post("/generate-synapse")
async def stream_data(chat: Chat, response: Response):
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    
    chat.chat_history.appendleft(system_msg)
    return StreamingResponse(generate_synapse(chat))
