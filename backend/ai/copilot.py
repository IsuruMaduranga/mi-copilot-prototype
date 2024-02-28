import re
import json
from typing import AsyncGenerator
from ai.agent import ChatAgent, QuestionGenerationAgent
from ai.llm import LLM
from models.base import Message, ChatResponse, Event

class Copilot():
    pattern = re.compile(r'```xml(.*?)```', re.DOTALL)
    
    def __init__(self):
        # Creating agents
        self.chat_agent = ChatAgent()
        self.question_agent = QuestionGenerationAgent()
        
    async def code_gen_chat(self, messages: Message) -> AsyncGenerator[ChatResponse, None]:
        response = ""
        async for chunk in await self.chat_agent.chat(messages):
            if(chunk):
                response += chunk
                yield ChatResponse(content=chunk, event=Event.CHAT_GENERATING).model_dump_json() + "\n"
        
        matches = re.findall(self.pattern, response)
        q = await self.question_agent.generate(messages, 1, bool(matches))
        try:
            parsed_q = json.loads(q)["questions"]
        except:
            yield ChatResponse(questions=[], event=Event.QUESTION_GENERATION_ERROR).model_dump_json() + "\n"
        else:
            yield ChatResponse(questions=parsed_q, event=Event.QUESTION_GENERATION_SUCCESS).model_dump_json() + "\n"
