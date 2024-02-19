import re
from openai import AsyncOpenAI
from app.models import Chat, Message, SynapseGenerationResponse
import toml

client = AsyncOpenAI()

with open("config.toml", "r") as f:
    config = toml.load(f)
    
with open("prompts/systemv2.prompt", "r") as f:
    system_msg_txt = f.read()
system_msg = Message(role="system", content=system_msg_txt)

with open("prompts/question_generation.prompt", "r") as f:
    generate_qustions_prompt = f.read()
    
with open("prompts/initial_question_generation.prompt", "r") as f:
    initial_generate_qustions_prompt = f.read()

pattern = re.compile(r'```xml(.*?)```', re.DOTALL)

async def generate_synapse(chat: Chat) -> str:
    chat.chat_history.insert(0, system_msg)        
    stream = await client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=list(chat.chat_history),
        stream=True,
    )
    response = ""
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            response += content
            yield SynapseGenerationResponse(content=content, questions=[]).model_dump_json() + "\n"
    ai_msg = Message(role="assistant", content=response)
    chat.chat_history.append(ai_msg)
    matches = re.findall(pattern, response)
    if matches:    
        questions = await generate_qustions(chat)
        yield SynapseGenerationResponse(content="", questions=questions).model_dump_json() + "\n"
    else:
        questions = await initial_generate_qustions(chat)
        yield SynapseGenerationResponse(content="", questions=questions).model_dump_json() + "\n"
            
async def generate_qustions(chat: Chat) -> str:
    usr_msg = Message(role="user", content=generate_qustions_prompt)
    chat.chat_history.append(usr_msg)
    response = await client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=list(chat.chat_history),
    )
    return response.choices[0].message.content.split("\n")

async def initial_generate_qustions(chat: Chat) -> str:
    usr_msg = Message(role="user", content=initial_generate_qustions_prompt)
    chat.chat_history.append(usr_msg)
    response = await client.chat.completions.create(
        model=config["openai"]["model"],
        seed=config["openai"]["seed"],
        temperature=config["openai"]["temperature"],
        messages=list(chat.chat_history),
    )
    return response.choices[0].message.content.split("\n")
