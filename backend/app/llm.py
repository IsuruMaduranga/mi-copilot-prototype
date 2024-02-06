from openai import AsyncOpenAI
from app.models import Chat, Message
import toml

client = AsyncOpenAI()

with open("config.toml", "r") as f:
    config = toml.load(f)
    
with open("prompts/system.prompt", "r") as f:
    system_msg_txt = f.read()
system_msg = Message(role="system", content=system_msg_txt)

async def generate_synapse(chat: Chat) -> str:
    chat.chat_history.insert(0, system_msg)        
    stream = await client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=list(chat.chat_history),
        stream=True,
    ) 
    async for chunk in stream:
        yield f"{chunk.choices[0].delta.content}"