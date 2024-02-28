import re
from typing import AsyncGenerator, List
from openai import AsyncOpenAI
from models.base import Message
from prompts.base import PromptFactory
import toml

class LLM():
    def __init__(self, model: str, seed: int, temperature: float):
        self.llm  = AsyncOpenAI()
        self.model = model
        self.seed = seed
        self.temperature = temperature
        
    async def chat(self, messages: List[Message], stream: bool = True, **kwargs) -> AsyncGenerator[str, None] | str:
        response_format =  { "type": "json_object" if kwargs.get("json_mode", False) else "text"}
        res = await self.llm.chat.completions.create(
            model=self.model,
            seed=self.seed,
            temperature=self.temperature,
            messages=messages,
            stream=stream,
            response_format=response_format
        )
        
        async def chat_stream():
            async for chunk in res:
                yield chunk.choices[0].delta.content
        if stream:
            return chat_stream()
        else:
            return res.choices[0].message.content
    
class LLMFactory():
    @classmethod
    def get_llm(cls, name) -> LLM:
        with open("config.toml", "r") as f:
            config = toml.load(f)
        return LLM(
            model=config["llm"][name]["model"],
            seed=config["llm"][name]["seed"],
            temperature=config["llm"][name]["temperature"]
        )
 