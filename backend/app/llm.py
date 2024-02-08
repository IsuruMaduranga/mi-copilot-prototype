from typing import List
from openai import AsyncOpenAI
import toml
from grpc_interfaces.copilot_pb2 import Chat, StringChunk
from app.helpers import role_to_string

client = AsyncOpenAI()

with open("config.toml", "r") as f:
    config = toml.load(f)
    
with open("prompts/system.prompt", "r") as f:
    system_msg_txt = f.read()
system_msg = {"role": "system", "content": system_msg_txt}

async def generate_synapse(chat: Chat) -> StringChunk:
    chat_history = [system_msg] + [dict(role=role_to_string(msg.role), content=msg.content) for msg in chat.messages]
    stream = await client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=chat_history,
        stream=True,
    ) 
    async for chunk in stream:
        print(chunk.choices[0].delta.content)
        yield StringChunk(data=chunk.choices[0].delta.content)
